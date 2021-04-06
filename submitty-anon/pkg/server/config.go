package server

type HTTPConfig struct {
	ListenAddress string
}

type Config struct {
	HTTP HTTPConfig
}
