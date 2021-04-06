package server

import (
	"net/http"

	"github.com/devplayer0/fyp/submitty-anon/pkg/util"
)

var (
	tplIndex      = util.LoadTemplate("index.html", "base.html")
	tplRegistered = util.LoadTemplate("registered.html", "base.html")
)

func (s *Server) viewIndex(w http.ResponseWriter, r *http.Request) {
	util.TemplateResponse(tplIndex, nil, w, http.StatusOK)
}

type registerInfo struct {
	Username string
	Password string
}

func (s *Server) viewRegister(w http.ResponseWriter, r *http.Request) {
	info := registerInfo{
		Username: "test",
		Password: "blah",
	}

	util.TemplateResponse(tplRegistered, info, w, http.StatusOK)
	//util.ErrResponse(w, errors.New("test error"), 0)
}
