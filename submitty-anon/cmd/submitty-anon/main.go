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
)

func main() {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	srv := server.NewServer(server.Config{
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
