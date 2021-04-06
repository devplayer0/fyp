package server

type SubmittyConfig struct {
	Semester string
	Course   string

	AccessLevel         int
	Group               int
	RegistrationSection int
}

type HTTPConfig struct {
	ListenAddress string
}

type Config struct {
	DBURL    string
	Submitty SubmittyConfig
	HTTP     HTTPConfig
}
