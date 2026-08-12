# 一.minio安装

**1.下载：https://www.minio.org.cn/download.shtml#/windows**  

<img src="..\image\1.png" style="zoom: 50%;" />

**2.任意创建好目录，把minio.exe放入目录中，并创建data目录**
![](..\image\2.png)

**3.打开该目录的cmd，输入如下命令**

.\minio.exe server  data目录 --console-address ":9001"

如：我的为 :      .\minio.exe server  D:\onlinerun\minio\data --console-address ":9001" 

![](..\image\3.png)

然后访问 ： http://localhost:9001  默认账号密码默认都是 minioadmin  看到如下画面则成功了

![](..\image\4.png)

---

# 二.Springboot整合

**1.引入依赖**

```xml
<dependencies>
    <!-- Spring Boot Web 启动器：提供 MVC、RESTful 接口、嵌入式 Tomcat 等 Web 开发核心能力 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring Boot 开发工具：支持热部署（自动重启）、LiveReload，提升开发效率，仅在运行时生效 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-devtools</artifactId>
        <scope>runtime</scope>
        <optional>true</optional>
    </dependency>

    <!-- Spring Boot 测试启动器：集成 JUnit、Mockito、AssertJ 等，用于单元测试和集成测试 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Lombok：通过注解自动生成 getter/setter、构造器、日志变量等，减少样板代码 -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>

    <!-- Knife4j（OpenAPI 3 版）：生成美观的 API 文档，支持在线调试，基于 Jakarta 规范 -->
    <dependency>
        <groupId>com.github.xiaoymin</groupId>
        <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
        <version>4.4.0</version>
    </dependency>

    <!-- MinIO 客户端：用于连接 MinIO 或兼容 S3 的对象存储服务，实现文件上传、下载和管理 -->
    <dependency>
        <groupId>io.minio</groupId>
        <artifactId>minio</artifactId>
        <version>8.5.17</version>
    </dependency>
</dependencies>
```

**2.添加minio相关配置（application.yml）**

```yaml
spring:
  application:
    name: minioback
server:
  port: 8080
minio:
  access-key: minioadmin
  secret-key: minioadmin
  endpoint: http://localhost:9000
  bucket: testminio
knife4j:
  setting:
    language: zh_cn
  enable: true
```

**3.创建配置类（不知道创建在哪里的看下面目录结构）**

```java
@Configuration
@ConfigurationProperties(prefix = "minio")
@Data
public class MinioConfig {
    private String endpoint;
    private String accessKey;
    private String secretKey;
    private String bucket;
    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
                .endpoint(endpoint)
                .credentials(accessKey, secretKey)
                .build();
    }
}
```

---

# 三.准备工作

**1.创建MinioService.并注入MinioConfig以及MinioClient**

```java
@Service
public class MinioService {
    @Autowired
    private MinioConfig minioConfig;
    @Autowired
    private MinioClient minioClient;
}
```

**目前的目录结构：**

![](..\image\5.png)

---

# **四.操作minio**

**如下方法都是在minioservice里面添加的**

## 1.上传文件

```java
	/**
     * 上传文件到MinIO
     * @param file 要上传的文件（Spring MultipartFile）
     * @return 文件在MinIO中的唯一标识（对象名称）
     */
    public String uploadFile(MultipartFile file) throws Exception {
        // 1. 检查存储桶是否存在，不存在则创建
        if (!minioClient.bucketExists(BucketExistsArgs.builder().bucket(minioConfig.getBucket()).build())) {
            minioClient.makeBucket(MakeBucketArgs.builder().bucket(minioConfig.getBucket()).build());
        }

        // 2. 生成唯一文件名（避免重名）
        String originalFilename = file.getOriginalFilename();
        String fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        String objectName = UUID.randomUUID().toString() + fileExtension;

        // 3. 上传文件
        minioClient.putObject(
                PutObjectArgs.builder()
                        .bucket(minioConfig.getBucket())          // 存储桶名称
                        .object(objectName)          // 对象名称（文件名）
                        .stream(file.getInputStream(), file.getSize(), -1)  // 文件流和大小
                        .contentType(file.getContentType())  // 文件类型
                        .build());
        return objectName;
        //返回结果：test/随机字符串.txt
    }
```

## 2.获取文件url(可通过浏览器访问)

```java
	/**
     * 获取文件临时访问URL（适合前端直接下载）
     * @param objectName 文件在MinIO中的唯一标识
     * @param expiry 有效期（单位：分钟）
     * @return 可访问的URL
     */
    public String getFileUrl(String objectName, int expiry) throws Exception {
        //objectName = "随机字符串.txt"
        return minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.GET)
                        .bucket(minioConfig.getBucket())
                        .object(objectName)
                        .expiry(expiry, TimeUnit.MINUTES)
                        .build());
        //返回结果：http://localhost:9000/bucket/随机字符串.txt?......
    }
```

## 3.删除文件

```java
 	/**
     * 删除文件
     * @param objectName 文件在MinIO中的唯一标识
     */
    public void deleteFile(String objectName) throws Exception {
        //objectName = "随机字符串.txt"
        minioClient.removeObject(
                RemoveObjectArgs.builder()
                        .bucket(minioConfig.getBucket())
                        .object(objectName)
                        .build());
    }
```

---

# 五.测试

## 1.创建控制层

创建**uploadFileController**

```java
@RestController
@RequestMapping("/upload")
public class UploadFileController {
    @Autowired
    private MinioService minioService;
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) {
        try {
            String objectName = minioService.uploadFile(file);
            return ResponseEntity.ok("文件上传成功，对象名称: " + objectName);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("文件上传失败: " + e.getMessage());
        }
    }
    @GetMapping("getUrl")
    public ResponseEntity<String> getFileUrl(@RequestParam String objectName) {
        try {
            String url = minioService.getFileUrl(objectName, 3600);
            return ResponseEntity.ok(url);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("获取文件URL失败: " + e.getMessage());
        }
    }
    // 删除文件
    @GetMapping("/delete")
    public ResponseEntity<String> deleteFile(@RequestParam String objectName) {
        try {
            minioService.deleteFile(objectName);
            return ResponseEntity.ok("文件删除成功");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("文件删除失败: " + e.getMessage());
        }
    }
}
```

当前目录

![](..\image\6.png)

## 2.启动项目访问

访问  http://localhost:8080/doc.html

看到如下画面就可以测试了：

![](..\image\7.png)

后面测试内容请看视频讲解

[配套网课](https://www.bilibili.com/video/BV1CWtJz1EcX?spm_id_from=333.788.player.switch&vd_source=e0c0ad2a316e90d4078b1131e8182407&p=5)

---
