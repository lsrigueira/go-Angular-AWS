package client

import (
	"bufio"
	"fmt"
	"os"

	"github.com/google/uuid"
	log "github.com/sirupsen/logrus"

	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cognitoidentityprovider"
	"github.com/aws/aws-sdk-go/service/sqs"
)

const (
	clientID = "4l5unarslkmjhn8lh8vrp41rfl"
)

var (
	reader = bufio.NewReader(os.Stdin)
)

type Client struct {
	session *session.Session
	sqs     *sqs.SQS
	svc     *sqs.SQS
	//TODO Quedan aca por siaca, pero creo que non necesito gardalos(non teria moito sentido a verdade)
	name      string
	password  string
	uuid      uuid.UUID
	UrlInbox  string
	UrlOutbox string
}

func NewClient() *Client {
	m := &Client{
		session: createSession(),
	}
	m.sqs = sqs.New(m.session)
	return m
}

func (clt *Client) RefreshSQSUrl() {
	var err error
	clt.UrlInbox, err = clt.getUrl("Inbox")

	if err != nil {
		log.Error(err)
	}
	clt.UrlOutbox, err = clt.getUrl("Outbox")
	if err != nil {
		log.Error(err)
	}
}
func (clt *Client) ReceiveMessage() (*sqs.Message, error) {

	timeout := int64(5)
	msgResult, err := clt.sqs.ReceiveMessage(&sqs.ReceiveMessageInput{
		AttributeNames: []*string{
			aws.String(sqs.MessageSystemAttributeNameSentTimestamp),
		},
		MessageAttributeNames: []*string{
			aws.String(sqs.QueueAttributeNameAll),
		},
		QueueUrl:            aws.String(clt.UrlOutbox),
		MaxNumberOfMessages: aws.Int64(1),
		VisibilityTimeout:   aws.Int64(timeout),
	})
	if err != nil {
		return nil, err
	}

	//return *msgResult.Messages[0].ReceiptHandle, nil
	if msgResult != nil {
		return msgResult.Messages[0], nil
	}
	return nil, nil
}
func (clt *Client) SendMessage(token, title, number string) {

	_, err := clt.sqs.SendMessage(&sqs.SendMessageInput{
		MessageAttributes: map[string]*sqs.MessageAttributeValue{
			"Token": &sqs.MessageAttributeValue{
				DataType:    aws.String("String"),
				StringValue: aws.String(token),
			},
			"Title": &sqs.MessageAttributeValue{
				DataType:    aws.String("String"),
				StringValue: aws.String(title),
			},
			"Number": &sqs.MessageAttributeValue{
				DataType:    aws.String("Number"),
				StringValue: aws.String(number),
			},
		},
		MessageBody:    aws.String("IThe atributes have all information"),
		QueueUrl:       aws.String(clt.UrlInbox),
		MessageGroupId: aws.String("GroupId" + number + strings.Replace(title, " ", "_", 100)),
	})
	if err != nil {
		log.Error("aqui")
		log.Error(err)
	}
}

func (clt *Client) getUrl(option string) (string, error) {
	result, err := clt.sqs.ListQueues(nil)
	if err != nil {
		log.Error(err)
	}
	for _, queueX := range result.QueueUrls {
		log.Error(*queueX)
		if strings.Contains(*queueX, option) {
			return *queueX, nil
		}
	}
	//log.Error(result)
	return "", fmt.Errorf("Cant find " + option + " queue")
}

func createSession() *session.Session {
	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	//return sqs.New(sess) *sqs.SQS
	return sess
}

func (clt *Client) LogIn(name, password string) error {
	svc := cognitoidentityprovider.New(clt.session)
	log.Errorf("name:" + name + "***")
	log.Errorf("passs:" + password + "***")
	params := &cognitoidentityprovider.SignUpInput{
		ClientId: aws.String(clientID),
		Password: aws.String(password),
		Username: aws.String(name),
	}
	req, resp := svc.SignUpRequest(params)
	err := req.Send()
	if err != nil {
		return err
	}
	if err == nil { // resp is now filled
		fmt.Println(resp)
	}
	return fmt.Errorf("Not able now")
}

func (clt *Client) Register(username, password string) error {
	svc := cognitoidentityprovider.New(clt.session)
	log.Errorf("name:" + username + "***")
	log.Errorf("passs:" + password + "***")
	params := &cognitoidentityprovider.AdminCreateUserInput{
		UserPoolId:        aws.String("us-east-1_M8lFiiZDR"),
		Username:          aws.String(username),
		TemporaryPassword: aws.String(password),
	}
	req, _ := svc.AdminCreateUserRequest(params)
	err := req.Send()
	if err != nil {
		return err
	}
	clt.name = username
	return nil
}
func (clt *Client) AskName() string {
	log.Info("Introduce the name: ")
	username, _ := reader.ReadString('\n')
	username = username[:len(username)-1]
	strings.Trim(username, " ")
	clt.name = username
	return username

}

func (clt *Client) AskPassword() string {
	log.Info("Introduce the password(6 char min): ")
	pass, _ := reader.ReadString('\n')
	pass = pass[:len(pass)-1]
	strings.Trim(pass, " ")
	clt.password = pass
	return pass
}

func (clt *Client) SetAnonymous() {

	clt.name = "Anonymous"
	clt.password = ""
	clt.uuid = uuid.New()
}
