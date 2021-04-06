package util

import "net/http"

func ErrToStatus(err error) int {
	switch {
	default:
		return http.StatusInternalServerError
	}
}
