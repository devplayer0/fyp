BINDATA_FLAGS = -fs -o internal/templates/bindata.go -pkg templates -prefix templates/ templates/...

.PHONY: all clean tools

default: bin/submitty-anon

tools:
	cat tools.go | sed -nr 's|^\t_ "(.+)"$$|\1|p' | xargs -tI % go get %

bin/%: tools
	go-bindata $(BINDATA_FLAGS)
	CGO_ENABLED=0 go build -o $@ ./cmd/$(shell basename $@)

dev/%: tools
	$(eval BIN = $(shell basename $@))
	go-bindata -debug $(BINDATA_FLAGS)
	CompileDaemon -exclude-dir=.git -build="go build -o bin/$(BIN) ./cmd/$(BIN)" -command bin/$(BIN)

clean:
	-rm -rf bin/
