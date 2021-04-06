package util

import (
	"fmt"
	"html/template"
	"net/http"

	log "github.com/sirupsen/logrus"

	"github.com/devplayer0/fyp/submitty-anon/internal/templates"
)

func LoadTemplate(names ...string) *template.Template {
	tpl := template.New(names[0])
	for _, name := range names {
		template.Must(tpl.Parse(string(templates.MustAsset(name))))
	}

	return tpl
}

var tplError = LoadTemplate("error.html", "base.html")

func TemplateResponse(tpl *template.Template, data interface{}, w http.ResponseWriter, statusCode int) {
	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(statusCode)

	if err := tpl.Execute(w, data); err != nil {
		log.WithError(err).Error("Failed to execute template")
		fmt.Fprint(w, "Failed to execute template")
	}
}

type errorInfo struct {
	Message string
}

func ErrResponse(w http.ResponseWriter, err error, statusCode int) {
	log.WithError(err).Error("Error while processing request")

	w.Header().Set("Content-Type", "text/html")
	if statusCode == 0 {
		statusCode = ErrToStatus(err)
	}
	w.WriteHeader(statusCode)

	tplError.Execute(w, errorInfo{err.Error()})
}
