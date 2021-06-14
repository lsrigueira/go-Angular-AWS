package main

import (
	client "goGin/client"
	"net/http"
	"path"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

func CORS(c *gin.Context) {

	// First, we add the headers with need to enable CORS
	// Make sure to adjust these headers to your needs
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Methods", "*")
	c.Header("Access-Control-Allow-Headers", "*")
	c.Header("Content-Type", "application/json")

	// Second, we handle the OPTIONS problem
	if c.Request.Method != "OPTIONS" {

		c.Next()

	} else {

		// Everytime we receive an OPTIONS request,
		// we just return an HTTP 200 Status Code
		// Like this, Angular can now do the real
		// request using any other method than OPTIONS
		c.AbortWithStatus(http.StatusOK)
	}
}

func main() {
	r := StartService()
	r.Use(CORS)
	r.GET("/recover", func(c *gin.Context) {
		myClient := client.NewClient()
		myClient.RefreshSQSUrl()
		myClient.SetAnonymous()
		token := myClient.GetID()
		ID, _ := c.GetQuery("ID")
		myClient.SendMessage(token, "Recover", ID, "0")
		var response string
	receiving:
		for {
			mapAtt := myClient.ReceiveMessage()

			if strings.Contains(mapAtt["Response"], "Error:") {
				log.Error(mapAtt["Response"])
				response = mapAtt["Response"]
			} else {
				log.Error("URL to download: " + mapAtt["Recover"])
				response = "Url para descarga: " + mapAtt["Response"] + "\n\n File to recover: " + mapAtt["Recover"]
			}

			break receiving
		}
		c.JSON(200, gin.H{
			"code":    "200",
			"message": response,
		})
	})
	r.GET("/buy", func(c *gin.Context) {
		myClient := client.NewClient()
		myClient.RefreshSQSUrl()
		myClient.SetAnonymous()
		token := myClient.GetID()
		ticketsnumber, _ := c.GetQuery("tickets")
		titulo, _ := c.GetQuery("titulo")
		log.Infof("Vamos a comprar " + ticketsnumber + " de " + titulo)
		myClient.SendMessage(token, "buy", titulo, ticketsnumber)
		var response string
	receiving:
		for {
			mapAtt := myClient.ReceiveMessage()

			if strings.Contains(mapAtt["Response"], "Error:") {
				log.Error(mapAtt["Response"])
				response = mapAtt["Response"]
			} else {
				log.Error("Url para descarga: " + mapAtt["Response"])
				log.Error("File to recover: " + mapAtt["Recover"])
				response = "Url para descarga: " + mapAtt["Response"] + "\n\n File to recover: " + mapAtt["Recover"]
			}

			break receiving
		}
		c.JSON(200, gin.H{
			"code":    "200",
			"message": response,
		})
		//c.Writer.WriteString("okey")
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
