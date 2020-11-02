package main

import (
	"bufio"
	client "clientaws/client"
	"fmt"
	"os"
	"strconv"
	"strings"

	log "github.com/sirupsen/logrus"
)

var (
	menuNumberOptions = 3
	reader            = bufio.NewReader(os.Stdin)
)

func main() {
	var option int
	for {
		printMenu()
		var err error
		option, err = getOption(menuNumberOptions)
		if err == nil {
			break
		}
		log.Error(err)
	}
	myClient := client.NewClient()
	log.Error(option)
	switch option {
	case 1:
		//name := "prueba"
		//password := "olaolaola"
		name := myClient.AskName()
		password := myClient.AskPassword()
		log.Error("Entramos en Login!!!")
		err := myClient.LogIn(name, password)
		if err != nil {
			log.Error(err)
		}
		os.Exit(0)
	case 2:
		name := myClient.AskName()
		password := myClient.AskPassword()
		err := myClient.Register(name, password)
		if err != nil {
			log.Error(err)
		}
		os.Exit(0)
	case 3:
		myClient.SetAnonymous()
	case 4:
		os.Exit(0)
	default:
	}

	myClient.RefreshSQSUrl()

	token := "TOKEN1"
	title := "Signal Procesing"
	ticketsnumber := "10"
	myClient.SendMessage(token, title, ticketsnumber)
	log.Error("ENviado")
	/*var Message *sqs.Message
	var err error
	loop:
	for {
		Message, err = myClient.ReceiveMessage()
		if err != nil {
			log.Errorf("Error receiving: %v", err)
		}
		log.Info("My message: %+v", Message.MessageAttributes)

		switch Message {
		case nil:

		default:
			break loop
		}
	}
	//log.Errorf("MENSAXE RECIBIDO: %+v", Message.MessageAttributes)
	log.Errorf("Identidade: %v", *Message.MessageAttributes["IdentityToken"].StringValue)
	log.Errorf("Resposta: %v", *Message.MessageAttributes["Response"].StringValue)
	*/
}

func printMenu() {
	log.Info("Choose one option:")
	log.Info("1) Log In")
	log.Info("2) Create Account")
	log.Info("3) Continue as Anonymous")
	log.Info("4) Exit")
	log.Info("Outro) PruebasRandom")

}

//getOption receive the number of valid options by argument
func getOption(numberOptions int) (int, error) {
	text, _ := reader.ReadString('\n')
	strings.Trim(text, " ")
	numberText := text[:1]
	finalNumber, err := strconv.Atoi(numberText)
	if err != nil || finalNumber > numberOptions {
		return 0, fmt.Errorf("Invalid Option")
	}
	return finalNumber, nil
}
