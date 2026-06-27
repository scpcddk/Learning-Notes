# 📦 Maven 核心笔记（Java 云原生 AI 方向）

---

## 1. Maven 是什么？

- **项目构建工具**：管理**依赖、编译、测试、打包、部署**
- **核心文件**：`pom.xml`（Project Object Model）

### **特点**

- **约定优于配置**：提供标准化的项目结构和构建生命周期
- **依赖管理**：自动处理项目依赖关系
- **插件体系**：丰富的插件支持各种构建任务
- **多模块支持**：简化大型项目的管理
- **中央仓库**：访问全球共享的库

> [!TIP]
> **核心心法**：依赖交给 Maven 管，打包交给 Maven 做，你只负责写好 Java 业务逻辑和 Dockerfile

---

## 2. 安装与配置

```bash
# 下载解压后配置环境变量
export MAVEN_HOME=/opt/maven
export PATH=$MAVEN_HOME/bin:$PATH

# 验证
mvn -v
```

**配置文件**：`~/.m2/settings.xml`（可配置阿里云镜像加速）

```xml
<settings>
    <mirrors>
        <mirror>
            <id>aliyun</id>
            <mirrorOf>central</mirrorOf>
            <url>https://maven.aliyun.com/repository/public</url>
        </mirror>
    </mirrors>
</settings>
```

---

## 3. ==常用 Maven 命令==

| 命令 | 说明 |
| ------ | ------ |
| `mvn clean` | 删除 `target/` 目录 |
| `mvn compile` | 编译 Java 代码 |
| `mvn test` | 执行测试用例 |
| `mvn package` | 打包成 JAR（或 WAR） |
| `mvn install` | 将 JAR 安装到本地仓库 |
| `mvn spring-boot:run` | 直接运行 Spring Boot 应用 |
| `mvn dependency:tree` | 查看依赖树（排冲突神器） |

> 💡 快速跳过测试：`mvn clean package -DskipTests`

---

## 4. **`pom.xml` 核心结构**（Spring Boot 示例）

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 坐标：唯一标识你的项目 -->
    <groupId>com.aiops</groupId>
    <artifactId>java-ai-gateway</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <!-- 父工程：Spring Boot 统一依赖管理 -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
    </properties>

    <dependencies>
        <!-- Spring Boot Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- 调用 AI API 所需（例如 OkHttp 或 SpringAI） -->
        <dependency>
            <groupId>com.squareup.okhttp3</groupId>
            <artifactId>okhttp</artifactId>
            <version>4.12.0</version>
        </dependency>

        <!-- 或者使用 SpringAI 官方 starter -->
        <!--
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
            <version>0.8.0</version>
        </dependency>
        -->
    </dependencies>

    <build>
        <plugins>
            <!-- Spring Boot 打包插件：生成可执行 fat jar -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

> [!IMPORTANT]
> **结构顺序**：`<properties>` → `<dependencies>` → `<build>` 符合 POM 规范

---

## 5. 依赖管理要点（避免踩坑）

### 5.1 scope 理解

| scope | 作用范围 | 典型场景 |
| ------- | --------- | --------- |
| `compile` | **默认**，全阶段生效，打包进 JAR | 大部分依赖 |
| `provided` | 编译测试需要，**打包时排除** | `lombok`、Servlet API（容器已提供） |
| `test` | 仅测试阶段使用 | `junit` |

### 5.2 排除传递依赖（解决冲突）

```xml
<dependency>
    <groupId>org.example</groupId>
    <artifactId>some-lib</artifactId>
    <exclusions>
        <exclusion>
            <groupId>com.conflict</groupId>
            <artifactId>bad-version</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

---

## 6. 生命周期与插件关系

| 阶段 | 执行插件目标 | 说明 |
| ------ | ------------- | ------ |
| `clean` | `maven-clean-plugin:clean` | 清理 target |
| `compile` | `maven-compiler-plugin:compile` | 编译源码 |
| `test` | `maven-surefire-plugin:test` | 执行测试 |
| `package` | `maven-jar-plugin:jar`（或 `spring-boot:repackage`） | 打包 |
| `install` | `maven-install-plugin:install` | 安装到本地仓库 |
| `deploy` | — | 上传到私服 |

> [!IMPORTANT]
> **调用规则**：`mvn 阶段`会自动执行该阶段之前的所有阶段。例如 `mvn package` 会先执行 `compile` → `test` → `package`

---

## 7. 针对目前项目的实战 Tips

### 📌 场景1：Docker 镜像中如何使用 Maven？

- **方案A（推荐）**：在本地用 `mvn clean package` 生成 `target/app.jar`，然后 COPY 进 Docker：

```dockerfile
FROM openjdk:17-jdk-slim
COPY target/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

- **方案B（多阶段构建）**：在 Dockerfile 内安装 Maven 编译（不推荐，镜像太重）

### 📌 场景2：如何用 Maven 管理不同环境配置（dev/prod）？

- 使用 `profiles`：

```xml
<profiles>
    <profile>
        <id>dev</id>
        <properties>
            <env>dev</env>
        </properties>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <env>prod</env>
        </properties>
    </profile>
</profiles>
```

运行时：`mvn clean package -Pdev`

### 📌 场景3：为什么 Spring Boot 打包后 JAR 很大？

- Spring Boot 插件会将所有依赖（包括 Tomcat）打成一个 **fat jar**。容器化部署时很合适，不需要外置 Tomcat

---

## 8. 常见错误及解决

| 错误信息 | 原因 | 解决方案 |
| --------- | ------ | --------- |
| `Could not find artifact` | 依赖下载失败 | 检查 mirror 配置，或手动下载到本地仓库 |
| `Unsupported class file major version 61` | JDK 版本不匹配 | 修改 `properties` 中的 `java.version` |
| `Main class not found` | 未指定启动类 | 在 `<properties>` 增加 `<start-class>` 或正常放置 `@SpringBootApplication` |
| `Package XXX does not exist` | 依赖未引入或 scope 错误 | 运行 `mvn dependency:tree` 检查 |

---

## 9. **核心记忆口诀**

> [!TIP]
> **坐标**定项目，**父工程**管版本，**依赖**看 scope，**打包**靠插件，**排错**用 tree，**跳过**加 `-DskipTests`

---

参考链接：[https://www.runoob.com/maven/maven-tutorial.html](https://www.runoob.com/maven/maven-tutorial.html)
