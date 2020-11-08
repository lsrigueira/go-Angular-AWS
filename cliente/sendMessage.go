package main

import (
	"bufio"
	client "clientaws/client"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

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
	myClient.RefreshSQSUrl()

	switch option {
	case 1:
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
		token := myClient.GetID()
		ticketsnumber := myClient.Ask("number of tickets")
		title := myClient.Ask("title")
		myClient.SendMessage(token, "buy", title, ticketsnumber)
		log.Error("Enviado")

	case 4:
		myClient.SetAnonymous()
		token := myClient.GetID()
		Identifier := myClient.Ask("Identifier")
		myClient.SendMessage(token, "Recover", Identifier, "0")
		os.Exit(0)
	default:
	}

	/*

	   O QUE ESTA DEBERIA SER TRANSPARENTE A COMPRAR, QUEDA DESLIGAR O BUCLE
	   PARA QUE O SEXA TAMEN A RECIBIR, TERIA SENTIDO METELO DENTOR DO
	   PROPIO CLIENTE XA QUE ESCOITA E DEVOLVE OS ARGUMENTOS. Despois querdaria
	   interpretar o resultado "solo"
	*/
/*receiving:
	for {
		message, err := myClient.ReceiveMessage()
		if err != nil {
			log.Error(err)
			time.Sleep(3 * time.Second)
			continue
		}
		mapAtt := myClient.GetAttributes(message)
		if !myClient.VerifyOwner(mapAtt) {
			log.Error("Message not for this client")
			myClient.LeaveMessage(message)
			time.Sleep(2 * time.Second)
			continue
		}
		myClient.DeleteMessage(message)
		print(mapAtt)
		if strings.Contains(mapAtt["Response"], "Error:") {
			log.Error(mapAtt["Response"])
		} else {
			log.Error("Url para descarga: " + mapAtt["Response"])
			log.Error("File to recover: " + mapAtt["Recover"])
		}

		break receiving
	}*/
}

func printMenu() {
	log.Info("Choose one option:")
	log.Info("1) Log In")
	log.Info("2) Create Account")
	log.Info("3) Continue as Anonymous")
	log.Info("4) Exit")
	log.Info("5) Recover a ticket")

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
