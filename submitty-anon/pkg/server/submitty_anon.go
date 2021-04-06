package server

import (
	"context"
	"net/http"
	"time"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

// Server represents the Submitty anonymous registration server
type Server struct {
	config Config

	http *http.Server
}

// NewServer creates a new iamd server
func NewServer(config Config) *Server {
	router := mux.NewRouter()
	s := &Server{
		config: config,

		http: &http.Server{
			Addr:    config.HTTP.ListenAddress,
			Handler: handlers.CustomLoggingHandler(nil, router, writeAccessLog),
		},
	}

	router.HandleFunc("/", s.viewIndex).Methods("GET")
	router.HandleFunc("/register", s.viewRegister).Methods("POST")

	return s
}

// Start starts the Submitty anonymous registration server
func (s *Server) Start() error {
	return s.http.ListenAndServe()
}

// Stop shuts down the Submitty anonymous registration server
func (s *Server) Stop() error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	return s.http.Shutdown(ctx)
}
