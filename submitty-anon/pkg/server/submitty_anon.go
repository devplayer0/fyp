package server

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	_ "github.com/jackc/pgx/v4/stdlib"
)

// Server represents the Submitty anonymous registration server
type Server struct {
	config Config

	db   *sql.DB
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
	var err error
	s.db, err = sql.Open("pgx", s.config.DBURL)
	if err != nil {
		return fmt.Errorf("failed to open main DB: %w", err)
	}

	return s.http.ListenAndServe()
}

// Stop shuts down the Submitty anonymous registration server
func (s *Server) Stop() error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	if err := s.db.Close(); err != nil {
		return fmt.Errorf("failed to close main DB: %w", err)
	}

	return s.http.Shutdown(ctx)
}
