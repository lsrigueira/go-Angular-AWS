package main

import (
	"fmt"
	"path"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	r := StartService()
	r.GET("/buy", func(c *gin.Context) {
		fmt.Print("ola")
	})
	r.GET("/GetTickets", func(c *gin.Context) {
		fmt.Print("ola")
	})

	err := r.Run(":5005")
	if err != nil {
		panic(err)
	}
}

func StartService() *gin.Engine {
	r := gin.Default()
	r.NoRoute(func(c *gin.Context) {
		dir, file := path.Split(c.Request.RequestURI)
		ext := filepath.Ext(file)
		if file == "" || ext == "" {
			c.File("./ui/html/index.html")
		} else {
			c.File("./ui/dist/ui/" + path.Join(dir, file))
		}
	})

	return r
}
