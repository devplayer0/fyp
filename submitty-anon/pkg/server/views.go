package server

import (
	"context"
	"fmt"
	"net/http"
	"strconv"

	nanoid "github.com/matoous/go-nanoid"
	log "github.com/sirupsen/logrus"
	"golang.org/x/crypto/bcrypt"

	"github.com/devplayer0/fyp/submitty-anon/pkg/util"
)

const usernameAlphabet = "0123456789abcdefghijklmnopqrstuvwxyz"

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

func (s *Server) register(ctx context.Context) (registerInfo, error) {
	info := registerInfo{}

	id, err := nanoid.Generate(usernameAlphabet, 8)
	if err != nil {
		return info, fmt.Errorf("failed to generate user ID: %w", err)
	}

	pw, err := nanoid.ID(16)
	if err != nil {
		return info, fmt.Errorf("failed to generate user password: %w", err)
	}
	pwHash, err := bcrypt.GenerateFromPassword([]byte(pw), bcrypt.DefaultCost)
	if err != nil {
		return info, fmt.Errorf("failed to hash user password: %w", err)
	}

	// PHP bcrypt hashes use 2y instead of 2y scheme...
	pwHash[2] = 'y'

	info = registerInfo{
		Username: fmt.Sprintf("anon%v", id),
		Password: pw,
	}

	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return info, fmt.Errorf("failed to begin db transaction: %w", err)
	}

	if _, err := tx.ExecContext(
		ctx,
		`INSERT INTO users (user_id, user_password, user_firstname, user_lastname, user_access_level, user_email, time_zone) VALUES ($1, $2, $3, $4, $5, $6, $7);`,
		info.Username, string(pwHash), "Anonymous", id, s.config.Submitty.AccessLevel, "", "Europe/Dublin",
	); err != nil {
		tx.Rollback()
		return info, fmt.Errorf("failed to write user into database: %w", err)
	}

	if _, err := tx.ExecContext(
		ctx,
		`INSERT INTO courses_users (semester, course, user_id, user_group, registration_section) VALUES ($1, $2, $3, $4, $5);`,
		s.config.Submitty.Semester, s.config.Submitty.Course, info.Username, s.config.Submitty.Group, strconv.Itoa(s.config.Submitty.RegistrationSection),
	); err != nil {
		tx.Rollback()
		return info, fmt.Errorf("failed to write user into course database: %w", err)
	}

	if err := tx.Commit(); err != nil {
		return info, fmt.Errorf("failed to commit to db: %w", err)
	}

	return info, nil
}

func (s *Server) viewRegister(w http.ResponseWriter, r *http.Request) {
	info, err := s.register(r.Context())
	if err != nil {
		util.ErrResponse(w, err, 0)
		return
	}

	log.WithFields(log.Fields{
		"username": info.Username,
		"password": info.Password,
	}).Info("Registered user")

	util.TemplateResponse(tplRegistered, info, w, http.StatusOK)
}
