# JavaWeb 极简前置笔记（为 SpringMVC 铺路）

> [!IMPORTANT]
> 浏览器/App发HTTP请求，先到Tomcat（Web容器），Tomcat把请求交给Servlet处理，而SpringMVC本质上就是一个封装好的“超级Servlet”，帮你自动做路由和数据绑定，让你不用手写繁琐的Servlet代码

---

## 1. HTTP 协议（接口开发只看这些）

### 1.1 请求 / 响应结构

#### (1)HTTP 请求报文（POST 方法，提交 JSON）

- **请求**：由**请求行**（方法 + URL）、**请求头**（额外信息，如数据格式）、**请求体**（传的数据）组成

```http
POST /api/user HTTP/1.1                              ← 请求行：方法 + URL
Host: example.com                                    ← 请求头：目标主机
Content-Type: application/json                       ← 请求头：数据格式（JSON）
Content-Length: 35                                   ← 请求头：请求体长度（字节）
User-Agent: Mozilla/5.0 (compatible; MyClient/1.0)   ← 请求头：客户端信息

{                                                    ← 空行（必须），下面是请求体
  "name": "张三",                                    ← JSON 数据，符合笔记 1.4
  "age": 20
}
```

#### (2)HTTP 响应报文（创建成功，状态码 200）

- **响应**：由**状态行**（状态码）、**响应头**、**响应体**（返回的数据）组成

```http
HTTP/1.1 200 OK                                     ← 状态行：版本 + 状态码 + 短语
Date: Mon, 08 Jun 2026 07:30:00 GMT                 ← 响应头：日期
Content-Type: application/json                      ← 响应头：返回的数据格式
Content-Length: 52                                  ← 响应头：响应体长度
Server: Apache-Coyote/1.1                           ← 响应头：服务器信息

{                                                    ← 空行，下面是响应体
  "code": 200,
  "message": "用户创建成功",
  "userId": 12345
}
```

> 接口开发中，我们主要关心请求方式、路径、携带的 JSON 数据，以及返回的状态码和 JSON

---

### 1.2 常用方法

- **GET**：从服务器**拿**数据，参数拼在 URL 后面
- **POST**：**提交**新数据，参数放在请求体里（通常用 JSON）

> 后续 SpringMVC 里用 `@GetMapping` / `@PostMapping` 就是基于它们

---

### 1.3 ==**最常用状态码**==

> 接口返回时一定要设置正确的状态码，前端靠这个判断成败

- **200**：一切正常，没有问题
- **400**（请求参数有误）：**客户端**传的参数格式不对、缺少必要字段、或数据校验不通过
- **404**（接口路径不存在）：**客户端**请求的 URL 写错了，或者接口已下线/未发布
- **500**（服务器内部出错）：**服务端**代码异常、数据库连接失败、依赖服务不可用等，是后端需要排查的
- **405**（方法不被允许）：**客户端**用了错误的 HTTP 方法（比如用 POST 去请求只支持 GET 的接口）
- **406**（不接受的响应类型）：**客户端**在 `Accept` 请求头里指定了服务器无法返回的格式（例如要求 `application/xml`，但服务器只支持 `application/json`），这属于客户端与服务器之间的内容协商失败，通常是客户端配置问题

> [!TIP]
> 看到 5xx 找后端，看到 4xx 先检查自己的请求

---

### 1.4 JSON 数据格式

前后端分离约定用 `application/json` 传数据，形式如：

```json
{
  "name": "张三",
  "age": 20
}
```

> Java 对象转 JSON，后来 SpringMVC 会自动帮我们完成（`@RestController` 功劳）

---

## 2. Servlet（SpringMVC 的底层核心）

### 2.1 核心概念

- **Servlet**：跑在`Tomcat`里的`Java`程序，专门用来接收和处理`Web`请求
- **HttpServlet**：专门处理`HTTP`请求的`Servlet`
  - `service()`方法：**请求入口**，`Tomcat`调用它来分发请求。它会根据`HTTP`方法（GET/POST 等）自动调用对应的 doXxx() 方法
  - `doGet()`：处理`GET`请求，从服务器**获取数据**时用
  - `doPost()`：处理`POST`请求，**提交新增数据**时用
  - `doPut() / doDelete()`：对应`RESTful`的**修改/删除**，原理一样，自己按需覆盖
- **HttpServletRequest**：代表**请求**，可以获取前端传来的参数、请求头等
- **HttpServletResponse**：代表**响应**，向浏览器写回数据（比如 JSON）

---

### 2.2 最简原生 Servlet（GET，返回 JSON）

以下使用 **jakarta.servlet**（SpringBoot3 配套），可直接运行：

```java
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet("/hello")
public class HelloServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // 告诉浏览器返回的数据是 JSON，编码用 UTF-8
        resp.setContentType("application/json;charset=UTF-8");

        // 手动拼一个 JSON 字符串
        String json = "{\"message\": \"你好，SpringMVC 的底层就是我\"}";

        PrintWriter out = resp.getWriter();
        out.write(json);
        out.flush();
    }
}
```

> 你会发现：每开发一个新接口都得新建一个类，还要手动拼 JSON、设置响应头，很麻烦

---

### 2.3 Maven 依赖（pom.xml）

```xml
<dependencies>
    <!-- Jakarta Servlet API，SpringBoot3 底层用的就是这个 -->
    <dependency>
        <groupId>jakarta.servlet</groupId>
        <artifactId>jakarta.servlet-api</artifactId>
        <version>6.0.0</version>
        <!-- provided：运行环境（Tomcat）已自带这个包，我们打包时不用带 -->
        <scope>provided</scope>
    </dependency>
</dependencies>
```

- `scope`是`provided`:最终程序要放到 Tomcat 容器里运行，Tomcat 自己已经包含了 Servlet 的 jar 包，你写的代码只需要在编译期能用就行，运行时用容器自带的，避免冲突
- 如果直接使用 SpringBoot 的 `spring-boot-starter-web`，这个依赖会被**自动传递引入**，无需手动加

---

## 3. Tomcat 容器

**一句话**：Tomcat 是一个**独立运行的 Web 容器**，负责接受网络请求、找到对应的 Servlet、返回响应，帮你屏蔽底层网络通信细节
> SpringBoot 内置了 Tomcat，所以启动时直接就能对外提供 HTTP 服务

---

## 4. Servlet vs SpringMVC（关键对比）

| 维度 | 原生 Servlet | SpringMVC |
| ------ | ------------ | ----------- |
| **一个接口一个类** | 必须新建类，继承 `HttpServlet` | 只需在方法上加注解（`@GetMapping`），多个接口可写在同一类中 |
| **获取参数** | 手动调用 `req.getParameter()`，类型转换自己写 | 直接写在方法参数里，自动接收并转换（支持 JSON 转对象） |
| **返回 JSON** | 手动拼接字符串，设置响应头 | 直接 return 对象，`@RestController` 自动转 JSON |
| **URL 映射** | 用注解 `@WebServlet`，路径写死 | 用 `@RequestMapping` 系列注解，支持动态路径（`/user/{id}`） |
| **代码量** | 大量模板式、重复代码 | 极简声明式，关注核心业务 |

---

**为什么学了 Servlet 再学 SpringMVC 更容易理解？**  

- 因为 SpringMVC 的核心 `DispatcherServlet` 本身就是继承自 `HttpServlet`，它只不过在 Servlet 基础上封装了**路由分发、参数绑定、JSON 转换**等常见操作。
- 了解 Servlet 的请求/响应对象后，你会瞬间明白 SpringMVC 帮我们省掉了多少脏活累活

---
