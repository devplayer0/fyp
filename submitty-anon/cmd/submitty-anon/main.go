package main

import (
	"flag"
	"os"
	"os/signal"
	"syscall"

	log "github.com/sirupsen/logrus"

	"github.com/devplayer0/fyp/submitty-anon/pkg/server"
)

var (
	httpListen = flag.String("listen", ":8080", "http listen address")

	submittySemester = flag.String("semester", "hilary21", "submitty semester")
	submittyCourse   = flag.String("course", "fyp21", "submitty course")

	submittyAccessLevel         = flag.Int("access-level", 3, "new user access level")
	submittyGroup               = flag.Int("group", 4, "new user group")
	submittyRegistrationSection = flag.Int("registration-section", 1, "new user registration section")
)

func main() {
	flag.Parse()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	srv := server.NewServer(server.Config{
		DBURL: os.Getenv("DB_URL"),
		Submitty: server.SubmittyConfig{
			Semester: *submittySemester,
			Course:   *submittyCourse,

			AccessLevel:         *submittyAccessLevel,
			Group:               *submittyGroup,
			RegistrationSection: *submittyRegistrationSection,
		},
		HTTP: server.HTTPConfig{
			ListenAddress: *httpListen,
		},
	})
	go func() {
		if err := srv.Start(); err != nil {
			log.WithError(err).Fatal("Failed to start server")
		}
	}()

	<-sigs
	if err := srv.Stop(); err != nil {
		log.WithError(err).Fatal("Failed to stop server")
	}
}
