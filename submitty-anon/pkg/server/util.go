package server

import (
	"io"

	"github.com/gorilla/handlers"
	log "github.com/sirupsen/logrus"
)

func writeAccessLog(w io.Writer, params handlers.LogFormatterParams) {
	log.WithFields(log.Fields{
		"remote":  params.Request.RemoteAddr,
		"agent":   params.Request.UserAgent(),
		"status":  params.StatusCode,
		"resSize": params.Size,
	}).Debugf("%v %v", params.Request.Method, params.URL.RequestURI())
}
