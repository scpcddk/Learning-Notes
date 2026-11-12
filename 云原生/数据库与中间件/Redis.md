# 《Redis 完整学习与开发速查笔记》

> **适用环境**　熟悉 MySQL 和 Spring Boot 基础。命令示例使用 Redis Open Source 7.x 的常用功能，容器仅供本地练习。
> **学习目标**　会选基本数据结构，写出带过期策略的旁路缓存，能说明缓存一致性、内存淘汰和故障恢复。
> **动手路线**　第 8～12 节覆盖持久化部署、ACL、并发限流、Streams 接管与排障。

---

# 第一篇　基础认知

## 1. Redis 适合处理什么

Redis 把常用数据结构放在内存中，提供低延迟的读写。电商目录可以把访问频繁的商品详情缓存几分钟，把短时计数放在 Redis。商品数据本身仍由 MySQL 持久化。系统也要规定 Redis 故障时哪些功能可以回源、哪些应限流。

| 类型 | 常用命令 | 用法 |
|---|---|---|
| String | `SET`、`GET`、`INCR` | 缓存 JSON，保存整数计数，原子加一 |
| Hash | `HSET`、`HGET`、`HGETALL` | 一个商品对象的多字段，按字段读写 |
| List | `LPUSH`、`LRANGE` | 最近事件列表，配合 `LTRIM` 限长 |
| Set | `SADD`、`SISMEMBER`、`SCARD` | 成员去重、判断商品是否属于某个活动 |
| Sorted Set | `ZADD`、`ZRANGE`、`ZREVRANGE` | 按分数排序，如按销量排行 |
| Stream | `XADD`、`XREADGROUP`、`XACK` | 保留事件序列，支持消费组和待确认列表 |

Redis 命令通常由主执行线程串行执行，因此单个 `INCR` 不会被其他客户端拆开。客户端先 `GET` 再 `SET` 是两条命令，两个并发请求可能覆盖彼此的更新。持久化和网络 I/O 还会涉及其他线程或子进程。

---

## 2. 过期、淘汰和持久化

| 机制 | 触发条件 | 关注点 |
|---|---|---|
| TTL 过期 | 键达到设定的失效时间 | 访问时检查和后台定期清理都可能删除已过期键 |
| 内存淘汰 | 内存达到 `maxmemory`，需要处理新写入 | 策略决定从哪些键中选，也可配置为拒绝相关写入 |
| RDB | 按配置或命令生成快照 | 恢复点取决于快照时间，故障可能丢失快照之后的写入 |
| AOF | 记录写操作并按策略刷盘 | 刷盘策略影响延迟和故障时的数据窗口，需要关注文件增长和重写 |

`TTL key` 返回 `-2` 表示键不存在，`-1` 表示没有过期时间。普通 `SET` 覆盖已有键时会清除 TTL，`SET key value EX 300` 可同时设置新值和有效期。缓存实例和重要会话实例的淘汰需求不同，应分别评估。

---

# 第二篇　操作与后端用法

## 3. 本地练习

```bash
# 练习容器，仅映射到本机地址
docker run --rm --name redis-lab -d -p 127.0.0.1:6379:6379 redis:7.4-alpine
docker exec -it redis-lab redis-cli
```

进入 `redis-cli` 后逐条执行。

**阅读提示**　在 Redis 交互终端逐条执行。先观察返回值，再根据键、TTL 或消费进度确认状态。

```text
PING
SET lab:sku:42 '{"name":"sku-42"}' EX 300
GET lab:sku:42
TTL lab:sku:42
HSET lab:order:42 status PAID totalCents 19900
HGET lab:order:42 status
INCR lab:metrics:demo:requests
ZADD lab:sales:ranking 8 sku-42 3 sku-10
ZREVRANGE lab:sales:ranking 0 1 WITHSCORES
```

预期 `PING` 返回 `PONG`，商品缓存的 TTL 为正，排行榜按 8、3 的顺序返回。再执行 `SET lab:sku:42 new-value`，观察 TTL 变为 `-1`，理解覆盖时的行为。练习结束后可 `docker stop redis-lab`。

---

## 4. Cache-Aside 旁路缓存

```text
读请求 → GET 商品缓存 → 命中则解析并返回
               ↓ 未命中
            查 MySQL → 带 TTL 回填 → 返回

写请求 → 修改 MySQL → 事务成功提交 → 删除对应缓存
```

```java
// 伪代码。ttlSeconds 可以加少量随机抖动，减少同一时刻集中到期。
Product getProduct(long id) {
    String key = "lab:sku:" + id;
    String cached = redis.get(key);
    if (cached != null) {
        return decode(cached);
    }
    Product product = productMapper.selectById(id);
    if (product != null) {
        redis.setWithTtl(key, encode(product), 300);
    }
    return product;
}
```

先提交数据库再删缓存可以缩小旧数据窗口。若并发读先查到旧版本、在删缓存之后才回填，旧值仍会存在一段时间。若删缓存失败，旧值也可能留到过期。可通过 TTL 控制时长，给失效动作加可追踪重试，要求更高时用可靠失效事件或版本校验。余额、权限等强一致场景需要单独评估是否绕过缓存。

### 4.1 在 Spring Boot 里落地

使用 Spring Boot 3.x BOM 管理 `spring-boot-starter-data-redis`，在 `application.yaml` 配置 Redis 连接。示例的超时值用于练习，部署时按 API 的总时限、网络延迟和回源容量调整。

```yaml
# 配置应用看到的 Redis 入口和等待预算，连接超时与读超时分别判断。
spring:
  data:
    redis:
      host: 127.0.0.1
      port: 6379
      connect-timeout: 500ms
      timeout: 300ms
```

注入 `StringRedisTemplate` 后，`opsForValue().get(key)` 读字符串，`opsForValue().set(key, json, Duration.ofMinutes(5))` 写值和 TTL，`delete(key)` 失效。对 Redis 超时设置明确的回源策略。低峰期可以限量回源，负载较高时需要保护 MySQL 的并发和连接数。

| 写缓存时机 | 为什么 |
|---|---|
| SQL 已执行、事务仍未提交 | 此时失效可能导致并发读重新缓存尚未提交前的旧值 |
| 本地事务已成功提交 | 适合触发缓存失效，例如使用 `AFTER_COMMIT` 监听。仍需覆盖进程退出或失效失败的窗口 |

---

## 5. 常见缓存故障

| 现象 | 触发方式 | 应对 |
|---|---|---|
| 缓存穿透 | 不存在的 ID 被反复查询 | 校验输入，短 TTL 缓存不存在状态，新增数据时也要失效对应空值 |
| 缓存击穿 | 一个热点键过期，大量请求同时回源 | 合并同键请求，限制回源并发，按业务允许范围预刷新 |
| 缓存雪崩 | 大批键同时过期，或实例整体不可用 | TTL 加抖动，设置超时和限流，给数据库留容量 |
| 热键 / 大键 | 少数键请求集中，或对象体积过大 | 分析访问和大小，缩小对象、分批处理或对热点做本地缓存 |

---

## 6. 原子操作和高可用边界

- `MULTI` / `EXEC` 批量执行排队命令，其他客户端无法插入队列执行过程。执行期某条命令报错时，已执行的命令不会回滚。`WATCH` 可对被观察的键做乐观并发控制。
- 单实例短期互斥可用 `SET key unique-token NX PX 5000` 获取锁，释放时需要原子比较 token 再删除。租期内任务如果没完成，其他客户端可取得锁。需要严格保护写入时，资源端还要使用版本校验或 fencing token。
- 主从复制提供副本，通常是异步的。Sentinel 负责非分片部署的监控与故障转移，Cluster 按哈希槽分片。涉及多键原子操作时检查是否要求同槽。高可用切换仍需按故障场景评估已确认写入丢失的可能性。

---

# 第三篇　排障与速查

## 7. 问题索引与命令表

| 问题 | 命令或证据 | 优先排查 |
|---|---|---|
| 键怎么提前没了 | `TTL`、`INFO stats` | 分辨过期、删除、淘汰，查看 `expired_keys` 与 `evicted_keys` |
| 内存为什么上涨 | `INFO memory`、`MEMORY USAGE key` | 找大对象、无 TTL 键和异常增长的前缀 |
| 单次命令慢 | `SLOWLOG GET 10` | 命令耗时与网络往返分别看，避免全量扫描 |
| 命中率下降 | `INFO stats` | 对同一时间窗比较命中和未命中增量，核对缓存键和 TTL |
| 生产如何查前缀 | `SCAN 0 MATCH lab:sku:* COUNT 100` | 使用返回的游标继续扫描，允许重复并在需要时去重 |

> [!warning]
> `KEYS *` 会一次遍历键空间，生产实例优先用分批 `SCAN`。`COUNT` 是工作量提示，单次返回数量可变化。

**L1** 能选数据类型并读懂 TTL。**L2** 给商品详情加旁路缓存。**L3** 复现并发回填旧值和 Redis 故障。**L4** 结合命中率、内存和数据丢失窗口评估持久化与高可用方案。

**记忆口诀**　读先查缓存，写提交后失效，过期控制旧值窗口，限流保护数据库。

---

# 第四篇　可复现部署与生产实践

## 8. 用 Compose 搭建带认证和持久化的实例

第 3 节的命令适合快速理解数据结构。这一节另建目录 `redis-lab/`，放置 `compose.yaml` 与 `redis.conf`，练习健康检查、配置文件、认证、数据卷和恢复。对外端口改为 `16379`，可与前面的 `6379` 并存。下面命令在 Bash 或 WSL 运行。

```yaml
# compose.yaml
services:
  redis:
    image: redis:7.4-alpine
    command:
      - redis-server
      - /usr/local/etc/redis/redis.conf
      - --requirepass
      - "${REDIS_LAB_PASSWORD:?export REDIS_LAB_PASSWORD first}"
    environment:
      REDISCLI_AUTH: "${REDIS_LAB_PASSWORD:?export REDIS_LAB_PASSWORD first}"
    ports:
      - "127.0.0.1:16379:6379"
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
      - redis-data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep -qx PONG"]
      interval: 5s
      timeout: 3s
      retries: 12
volumes:
  redis-data:
```

```conf
# redis.conf
bind 0.0.0.0
protected-mode yes
dir /data

save 300 1
appendonly yes
# AOF 每秒尝试刷盘，异常停机时仍可能丢失最近的写入。
appendfsync everysec

maxmemory 128mb
maxmemory-policy noeviction

slowlog-log-slower-than 10000
slowlog-max-len 128
```

```bash
# 仅用于该练习。在当前终端输入一个自定义口令
read -rs -p 'Redis lab password: ' REDIS_LAB_PASSWORD
printf '\n'
export REDIS_LAB_PASSWORD

docker compose up -d
docker compose ps
docker compose exec redis redis-cli PING
docker compose exec redis redis-cli SET lab:sku:42 '{"version":1,"priceCents":19900}'
docker compose exec redis redis-cli INFO persistence

# 重建服务，继续使用同一个命名卷
docker compose up -d --force-recreate redis
docker compose exec redis redis-cli GET lab:sku:42
```

等状态健康后再执行 CLI。预期 `PING` 返回 `PONG`，重建后键仍可读取。宿主应用连接 `127.0.0.1:16379`，同一个 Compose 网络中的应用连接 `redis:6379`。练习配置把认证值放在容器参数和环境中，具备容器管理权限的人可查看。实际部署按平台接入 Secret、ACL 文件与 TLS，并只开放应用需要的网络路径。

> [!note]
> `docker compose down` 默认保留命名卷。容器重建和正常关闭适合验证挂载，突然断电的数据损失边界需要独立演练。删除练习卷前先确认其中没有要保留的数据。

### 8.1 用 ACL 分离运维和应用权限

```bash
# 下面用一次性的练习账号和口令，仅授权读取 lab:sku:*。
docker compose exec redis redis-cli ACL SETUSER catalog-reader reset on \
  '>reader-lab-pass' '~lab:sku:*' '-@all' '+ping' '+get' '+ttl'

docker compose exec -e REDISCLI_AUTH=reader-lab-pass redis \
  redis-cli --user catalog-reader GET lab:sku:42

# 正例可以 GET。以下两条分别因为键范围和命令权限而被拒绝。
docker compose exec -e REDISCLI_AUTH=reader-lab-pass redis \
  redis-cli --user catalog-reader GET lab:order:42
docker compose exec -e REDISCLI_AUTH=reader-lab-pass redis \
  redis-cli --user catalog-reader SET lab:sku:42 overwrite

docker compose exec redis redis-cli ACL LOG 5
```

`ACL SETUSER` 默认在已有规则上修改，练习中的 `reset` 让多次执行结果一致。运行时修改 ACL 后，进程重启是否保留取决于 ACL 文件或配置的保存方式。生产环境用声明的配置管理账号，验证新账号后再回收旧权限。出现 `NOAUTH` 先核对是否发送认证，`WRONGPASS` 核对用户名和凭据，`NOPERM` 再看用户允许的命令和键模式。

---

## 9. 并发控制练习

### 9.1 观察 WATCH 如何发现并发写

在两个终端执行 `docker compose exec redis redis-cli`。以下命令在 Redis 交互终端执行。先把 `lab:stock:42` 设为 8。

| 步骤 | 客户端 A | 客户端 B |
|---|---|---|
| 1 | `WATCH lab:stock:42`，`GET lab:stock:42` 得到 8 | 等待 |
| 2 | `MULTI`，`SET lab:stock:42 7`，得到 `QUEUED` | `DECR lab:stock:42`，得到 7 |
| 3 | `EXEC`，事务被取消 | `GET lab:stock:42` 仍为 7 |
| 4 | 重新 `WATCH`、读 7、计算 6 后提交 | 等待 |

`WATCH` 跟随连接，Spring Data Redis 中要保证 WATCH、读取、MULTI、EXEC 在同一连接上执行。竞争大时限制重试次数并加退避。若条件判断只依赖少数 Redis 键，短脚本可避免多次往返。关键库存仍建议由持久化事务和数据约束决定。

### 9.2 用 Lua 实现有 TTL 的固定窗口限流

下面的练习每个键第一次访问时建立窗口，窗口内最多放行 3 次。超过次数仍计数，但不会延长窗口。多客户端执行脚本时，计数和设定 TTL 在 Redis 端一次完成，避免应用在 `INCR` 和 `PEXPIRE` 之间退出留下无过期计数器。

```lua
-- limit.lua。KEYS[1] 为限流键，ARGV 分别为窗口毫秒和最大次数。
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
if not window or not limit or window < 1 or limit < 1
   or window % 1 ~= 0 or limit % 1 ~= 0 then
  return redis.error_reply("window and limit must be positive integers")
end

local n = redis.call("INCR", KEYS[1])
local remaining = redis.call("PTTL", KEYS[1])
if remaining < 0 then
  redis.call("PEXPIRE", KEYS[1], window)
  remaining = window
end

local allowed = 0
if n <= limit then
  allowed = 1
end
return {allowed, n, remaining}
```

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
script_sha="$(docker compose exec -T redis redis-cli -x SCRIPT LOAD < limit.lua)"
for _ in 1 2 3 4; do
  docker compose exec -T redis redis-cli EVALSHA "$script_sha" 1 lab:rate:user-42 60000 3
done
```

`EVALSHA` 参数中数字 `1` 表示后面紧跟一个 key，其余是 `ARGV`。结果依次为放行 1、1、1、0，第三个值是当前剩余毫秒。重新运行前可等窗口过期，或只删除本练习的限流键。

> [!warning]
> Lua 执行期间会阻塞其他命令执行。把脚本保持为短小、常量级操作，业务重试不应重复消耗外部副作用。固定窗口在相邻两个窗口边界可形成突发，要求更平滑时再评估滑动窗口或令牌桶。

`SCRIPT LOAD` 的缓存可能因重启、故障切换或清理消失，客户端要识别 `NOSCRIPT` 并重新加载或改用 `EVAL`。Redis Cluster 中多个键参与同一个脚本时应落在同一槽，可用明确的 hash tag，例如 `stock:{42}:available` 与 `stock:{42}:reservations`。不能用同一个 hash tag 装下全部业务键，否则会产生热点槽。

### 9.3 锁的释放和失效窗口

获取锁时写入每次生成的唯一 token。客户端超时后，旧锁可能已过期，新客户端已经持有同名锁。释放使用比较加删除脚本。

```lua
-- unlock.lua。客户端只释放自己仍持有的锁。
if redis.call("GET", KEYS[1]) == ARGV[1] then
  return redis.call("DEL", KEYS[1])
end
return 0
```

用两个客户端做实验。A 取得 1 秒锁，等待超过租期。B 用新 token 取得锁。A 执行释放脚本，预期返回 0，B 的锁仍在。A 即使无法误删锁，也可能在租期过后继续执行旧任务。需要防止旧写入覆盖时，把版本或 fencing token 传到数据库，由资源端检查。涉及本地状态变更时优先考虑数据库唯一约束和条件更新。

---

## 10. Streams 消费组与待确认恢复

Streams 适合在 Redis 内保留一个有限的事件流。组内多个 worker 分工。读取后消息进入 Pending Entries List（PEL），成功处理后显式确认。以下命令使用交互式 `redis-cli`，应在第 8 节实例中执行。

**阅读提示**　在 Redis 交互终端逐条执行。先观察返回值，再根据键、TTL 或消费进度确认状态。

```text
XGROUP CREATE lab:stock:events stock-workers 0 MKSTREAM
XADD lab:stock:events * eventId evt-42 sku 42 delta -1
XREADGROUP GROUP stock-workers worker-a COUNT 1 STREAMS lab:stock:events >
XPENDING lab:stock:events stock-workers
```

`>` 请求组从未分配过的新消息。此时模拟 worker-a 在落库之前退出，暂不执行 `XACK`。等待至少 1 秒，用 worker-b 接管。

**阅读提示**　在 Redis 交互终端逐条执行。先观察返回值，再根据键、TTL 或消费进度确认状态。

```text
XAUTOCLAIM lab:stock:events stock-workers worker-b 1000 0-0 COUNT 10
XPENDING lab:stock:events stock-workers - + 10
XACK lab:stock:events stock-workers <上一条输出中的消息ID>
XPENDING lab:stock:events stock-workers
```

预期认领后 owner 变为 worker-b，处理并确认后待确认数量为 0。持续恢复时要沿用 `XAUTOCLAIM` 的下一游标继续扫描，到 `0-0` 后仍可在下轮重新扫描。认领闲置阈值要大于正常任务的最长处理时间，否则正常 worker 和接管 worker 可能同时处理。按业务 `eventId` 去重，把结果先持久化，再 ACK。

| 操作 | 边界 |
|---|---|
| `XACK` | 从消费组的 PEL 中移除引用，事件仍可存在于 Stream |
| `XDEL` / `XTRIM` | 改变 Stream 数据。修剪可能移除尚未处理的正文，需要一起检查恢复窗口 |
| `XPENDING` | 看已分配但未确认的记录，未分配的新记录需用组信息和消费速率另行判断 |
| `XINFO GROUPS` | 看组进度、消费者与 lag。数值需结合修剪和组初始位置解释 |
| 可靠通知 | 按最长离线时间、重试、保留和恢复能力选型。跨组长时间回放可对比 Kafka |

---

## 11. 持久化、复制和恢复决策

| 场景 | 方案起点 | 要实际测的故障 |
|---|---|---|
| 可重建的商品缓存 | TTL、内存上限和 LFU/LRU。持久化按回源容量决定 | 整个 Redis 为空时的请求量、DB 连接数和预热速度 |
| 会话或短时工作状态 | 分开实例。选择持久化、复制、禁止随意淘汰 | 主从切换后会话丢失窗口，应用重连与过期 |
| 需要分摊内存和吞吐 | Cluster，多节点按槽分布 | 热点槽、跨槽命令、客户端拓扑刷新和扩容迁移 |
| 单主从部署自动切换 | Sentinel，客户端通过 Sentinel 找当前主节点 | 主节点断连、网络分区、切换时的写入和恢复 |

`appendfsync everysec` 是常见折中，故障时通常可能丢失最近约一秒写入，实际情况与磁盘和系统状态相关。Redis 7 多段 AOF 需要按官方方式备份整个 AOF 目录与 manifest，在线复制之前先处理重写竞争。使用 `BGSAVE` 生成 RDB 时，先查看 `INFO persistence` 的最后保存状态与后台进程。把备份恢复到独立实例，核对代表性键、TTL、抽样数据和客户端兼容后再依赖它。

`WAIT` 可等待复制确认，无法把异步复制部署变为强一致系统。主从拓扑和快照都不能代替定期恢复演练。记录允许丢多少数据（RPO）和允许多长时间恢复（RTO），据此选择备份频率与恢复路径。

### 11.1 Pipeline、事务和 Lua 怎么选

| 方式 | 主要解决 | 结果和边界 |
|---|---|---|
| Pipeline | 多条命令减少网络往返 | 逐条执行并返回结果，其他客户端可能在命令间执行 |
| `MULTI / EXEC` | 一组命令连续执行 | 执行时错误不会回滚其他成功命令 |
| `WATCH + MULTI / EXEC` | 读后写时发现并发变化 | 键变化时取消事务，由客户端决定是否重试 |
| Lua | 让判断与修改在服务端一起完成 | 短脚本适合限流和条件更新，长脚本会阻塞其他操作 |

Python 的 redis-py 默认 Pipeline 可带事务语义。下面显式指定 `transaction=False`，在第 8 节实例中执行，观察返回值与命令的顺序一致。先安装项目所需的 `redis` 客户端，并沿用练习口令环境变量。

```python
import os
from redis import Redis

# 连接第 8 节 Compose 的宿主入口，使用已有练习凭据。
client = Redis(host="127.0.0.1", port=16379,
               password=os.environ["REDIS_LAB_PASSWORD"], decode_responses=True)
with client.pipeline(transaction=False) as batch:
    batch.set("lab:sku:batch-demo", "available", ex=60) # SET 后的值只保留 60 秒
    batch.get("lab:sku:batch-demo")                    # 与 SET 一起发送，结果仍按顺序返回
    created, value = batch.execute()

print(created, value)  # 预期 True available
```

批次太大时，客户端与 Redis 都可能积累大量结果，增加内存和尾延迟。先按几百条量级分批做基准，再根据对象大小、并发、网络延迟和 p99 调整。依赖前一个结果的操作应拆批，或由短 Lua 脚本表达。

### 11.2 Redis Cluster 的重定向和多键约束

Cluster 用 16384 个哈希槽划分键。普通客户端第一次找错节点时，`MOVED` 表示应该按新地址处理该槽并刷新路由。迁移期间收到 `ASK` 时，客户端到指定节点发送 `ASKING` 后重试该次操作，不应据此永久改写槽路由。生产使用支持 Cluster 的客户端，并确保它拿到的节点地址从应用网络可达。

`stock:{42}:available` 与 `stock:{42}:reserved` 使用同一个 hash tag，适合需要同槽的多键操作。跨槽的 `MGET`、事务或 Lua 在服务端会受到同槽限制。客户端若自动拆成多次操作，仍需按独立请求理解部分失败和原子性。 [Redis Pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/) · [Redis Cluster 规范](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

---

## 12. 性能定位与验收

### 12.1 先判断慢在服务器还是客户端

```bash
# 在已运行容器内执行命令，命令使用容器里的路径和网络。
docker compose exec redis redis-cli INFO memory
docker compose exec redis redis-cli INFO stats
docker compose exec redis redis-cli INFO replication
docker compose exec redis redis-cli SLOWLOG GET 10
docker compose exec redis redis-cli LATENCY DOCTOR
docker compose exec redis redis-cli MEMORY USAGE lab:sku:42
docker compose exec redis redis-cli --scan --pattern 'lab:sku:*'
```

| 观测 | 判断 | 处置顺序 |
|---|---|---|
| 客户端 p99 高，慢日志少 | 可能卡在连接池、网络、线程排队或读取大响应 | 核对连接等待、网络延迟和对象大小 |
| 慢日志频繁出现大范围命令 | 服务端执行时间高 | 按业务拆小范围读写，避免一次取全量，观察同时间段 CPU |
| 内存接近上限，淘汰增长 | 先查数据规模、无 TTL 键、写入速度 | 看失效和命中率，再调整容量、淘汰策略或键结构 |
| RSS 明显高于数据内存 | 检查分配器碎片、后台重写、复制缓冲和 fork 峰值 | 结合绝对内存、延迟和系统余量判断 |
| 重启后回源压力暴涨 | 缓存冷启动，应用大量穿透 | 逐步恢复流量，限制并发，预热最热的一批键 |

`SLOWLOG` 主要看 Redis 执行命令的耗时，客户端耗时还包含网络等因素。`LATENCY DOCTOR` 要有延迟监控样本才有诊断结果，练习可用 `CONFIG SET latency-monitor-threshold 5` 临时开启，再观察实际操作。线上避免在高峰用 `MONITOR`、全量扫描或大规模基准测试。扫描、抓日志和基准应先在隔离实例中做。

### 12.2 五个实战验收项

1. **部署与持久化**　保存两个有代表性的键，重建容器，记录检查结果。解释正常重建与意外停机有什么差别。
2. **权限**　只读账号可读取匹配前缀，越权访问和写入分别得到拒绝证据。
3. **限流**　同一账号连续四次只放行前三次，窗口到期后能恢复。尝试两个账号，确认计数各自独立。
4. **消费恢复**　制造一条未 ACK 的消息，另一个 worker 能接管。重复处理同一个事件时业务结果只写一次。
5. **故障定位**　在练习实例分别制造端口错误、错误口令、连接超时，给出客户端报错、服务端状态、最终修复和复测结果。

官方实操　[Redis ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/) · [Lua 脚本](https://redis.io/docs/latest/develop/programmability/eval-intro/) · [Streams](https://redis.io/docs/latest/develop/data-types/streams/) · [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/)

延伸阅读　[MySQL](MySQL/基础知识/MySQL.md) · [Cache-Aside](https://redis.io/docs/latest/develop/use-cases/cache-aside/) · [键淘汰](https://redis.io/docs/latest/reference/eviction/) · [持久化](https://redis.io/docs/latest/management/persistence/) · [事务](https://redis.io/docs/latest/develop/using-commands/transactions/) · [Spring Boot 配置项](https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html)
