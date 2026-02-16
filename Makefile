# Tool versions
ACTIONLINT_VERSION := 1.7.10
ACTION_VALIDATOR_VERSION := 0.8.0
GH_AW_VERSION := v0.45.0

# Helper: Detect OS and architecture (sets OS and ARCH variables)
# Usage: $(DETECT_OS_ARCH)
DETECT_OS_ARCH = OS=$$(uname -s | tr '[:upper:]' '[:lower:]'); \
	ARCH=$$(uname -m); \
	case "$$ARCH" in \
		x86_64) ARCH="amd64" ;; \
		arm64|aarch64) ARCH="arm64" ;; \
	esac

# Helper: Download a file using curl or wget
# Usage: $(call download-file,URL,OUTPUT_FILE)
# For tar.gz extraction: $(call download-file,URL) | tar -xz -C bin actionlint
# For direct binary: $(call download-file,URL,OUTPUT_FILE)
define download-file
	if command -v curl >/dev/null 2>&1; then \
		if [ -n "$(2)" ]; then \
			curl -sSL "$(1)" -o "$(2)"; \
		else \
			curl -sSL "$(1)"; \
		fi; \
	elif command -v wget >/dev/null 2>&1; then \
		if [ -n "$(2)" ]; then \
			wget -qO "$(2)" "$(1)"; \
		else \
			wget -qO- "$(1)"; \
		fi; \
	else \
		echo "Error: curl or wget required"; \
		exit 1; \
	fi
endef

.PHONY: help setup setup-actionlint setup-action-validator setup-gh setup-gh-macos setup-gh-debian setup-gh-aw compile sync lint-workflows lint-actions release

help:
	@echo "This repository contains GitHub Actions workflows and gh-agent-workflows templates."
	@echo "Edit claude-workflows/*/action.yml (composite actions) or gh-agent-workflows/*.md (agentic workflows)."
	@echo ""
	@echo "Available targets:"
	@echo "  setup                - Set up development environment (install tools)"
	@echo "  setup-actionlint     - Install actionlint tool"
	@echo "  setup-action-validator - Install action-validator tool"
	@echo "  setup-gh             - Check GitHub CLI installation"
	@echo "  lint-workflows       - Validate GitHub Actions workflow files"
	@echo "  lint-actions         - Validate GitHub Actions composite action files"
	@echo "  sync                 - Run scripts/dogfood.sh to copy shims, prompts, and fragments"
	@echo "  compile              - Sync files + compile agentic workflows to lock files"
	@echo "  lint                 - Run all linters"
	@echo "  release VERSION=x.y.z - Create and push a new release tag"

setup: setup-actionlint setup-action-validator setup-gh setup-gh-aw
	@echo ""
	@echo "✓ Setup complete!"

setup-gh:
	@echo "Checking GitHub CLI..."
	@if command -v gh >/dev/null 2>&1; then \
		echo "✓ GitHub CLI found: $$(gh --version | head -1)"; \
	elif [ -n "$$CI" ] || [ -n "$$GITHUB_ACTIONS" ]; then \
		$(MAKE) setup-gh-debian; \
	else \
		OS="$$(uname -s | tr '[:upper:]' '[:lower:]')"; \
		case "$$OS" in \
			darwin) $(MAKE) setup-gh-macos ;; \
			linux) \
				if command -v apt-get >/dev/null 2>&1; then \
					$(MAKE) setup-gh-debian; \
				else \
					echo "⚠ GitHub CLI not found. This installer supports Debian/Ubuntu (apt-get)."; \
					echo "  For other Linux distributions, see: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"; \
				fi \
				;; \
			*) \
				echo "⚠ GitHub CLI not found. Install with:"; \
				echo "  macOS:   brew install gh"; \
				echo "  Linux:   See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"; \
				echo "  Windows: See https://github.com/cli/cli/blob/trunk/docs/install_windows.md"; \
				echo "  Or visit: https://cli.github.com/"; \
				;; \
		esac; \
	fi

setup-gh-macos:
	@echo "Installing GitHub CLI for macOS..."
	@if command -v brew >/dev/null 2>&1; then \
		brew install gh && \
		echo "✓ GitHub CLI installed"; \
	else \
		echo "Error: Homebrew not found. Install Homebrew first:"; \
		echo "  /bin/bash -c \"$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""; \
		exit 1; \
	fi

setup-gh-debian:
	@echo "Installing GitHub CLI for Debian/Ubuntu..."
	@sudo apt-get update && \
	type -p curl >/dev/null || sudo apt-get install -y curl && \
	curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
	sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
	echo "deb [arch=$$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
	sudo apt-get update && \
	sudo apt-get install -y gh && \
	echo "✓ GitHub CLI installed"

setup-gh-aw:
	@echo "Setting up gh-aw compiler..."
	@if command -v go >/dev/null 2>&1; then \
		echo "Installing gh-aw $(GH_AW_VERSION)..."; \
		GOBIN="$$(pwd)/bin" go install github.com/github/gh-aw/cmd/gh-aw@$(GH_AW_VERSION) && \
		echo "✓ gh-aw installed to bin/gh-aw"; \
	else \
		echo "⚠ Go not found. Install Go first: https://go.dev/dl/"; \
		exit 1; \
	fi

sync:
	@./scripts/dogfood.sh

compile: setup-gh-aw sync
	@echo "Compiling agentic workflows..."
	@bin/gh-aw compile --action-tag $(GH_AW_VERSION)

setup-actionlint:
	@echo "Setting up actionlint..."
	@mkdir -p bin
	@ACTIONLINT_VERSION="$(ACTIONLINT_VERSION)"; \
	ACTIONLINT_BIN="bin/actionlint"; \
	if [ -f "$$ACTIONLINT_BIN" ]; then \
		echo "✓ actionlint already installed: $$($$ACTIONLINT_BIN --version 2>&1 | head -1)"; \
	else \
		echo "Downloading actionlint v$$ACTIONLINT_VERSION..."; \
		$(DETECT_OS_ARCH); \
		URL="https://github.com/rhysd/actionlint/releases/download/v$$ACTIONLINT_VERSION/actionlint_$${ACTIONLINT_VERSION}_$${OS}_$${ARCH}.tar.gz"; \
		echo "Downloading from $$URL..."; \
		$(call download-file,$$URL) | tar -xz -C bin actionlint && chmod +x "$$ACTIONLINT_BIN" && \
		echo "✓ actionlint installed to $$ACTIONLINT_BIN"; \
	fi

lint-workflows: setup-actionlint
	@echo "Validating GitHub Actions workflow files..."
	@ACTIONLINT="bin/actionlint"; \
	find claude-workflows .github/workflows -name "example.yml" -o -name "example.yaml" 2>/dev/null | while read -r file; do \
		echo "Checking $$file..."; \
		$$ACTIONLINT "$$file" || exit 1; \
	done

setup-action-validator:
	@echo "Setting up action-validator..."
	@mkdir -p bin
	@ACTION_VALIDATOR_VERSION="$(ACTION_VALIDATOR_VERSION)"; \
	ACTION_VALIDATOR_BIN="bin/action-validator"; \
	if [ -f "$$ACTION_VALIDATOR_BIN" ]; then \
		echo "✓ action-validator already installed: $$($$ACTION_VALIDATOR_BIN --version 2>&1 | head -1)"; \
	else \
		echo "Downloading action-validator v$$ACTION_VALIDATOR_VERSION..."; \
		$(DETECT_OS_ARCH); \
		URL="https://github.com/mpalmer/action-validator/releases/download/v$$ACTION_VALIDATOR_VERSION/action-validator_$${OS}_$${ARCH}"; \
		echo "Downloading from $$URL..."; \
		$(call download-file,$$URL,$$ACTION_VALIDATOR_BIN) && chmod +x "$$ACTION_VALIDATOR_BIN" && \
		echo "✓ action-validator installed to $$ACTION_VALIDATOR_BIN"; \
	fi

lint-actions: setup-action-validator
	@echo "Validating GitHub Actions composite action files..."
	@ACTION_VALIDATOR="bin/action-validator"; \
	find claude-workflows base -name "action.yml" -o -name "action.yaml" 2>/dev/null | while read -r file; do \
		echo "Checking $$file..."; \
		$$ACTION_VALIDATOR "$$file" || exit 1; \
	done

lint: lint-workflows lint-actions

# Release a new version
# Usage: make release VERSION=1.0.0
release:
ifndef VERSION
	@echo "Error: VERSION is required"
	@echo "Usage: make release VERSION=1.0.0"
	@echo ""
	@echo "Recent tags:"
	@git tag --sort=-version:refname | head -10
	@exit 1
endif
	@echo "Creating release v$(VERSION)..."
	@if ! echo "$(VERSION)" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$$'; then \
		echo "Error: VERSION must be in semver format (e.g., 1.0.0)"; \
		exit 1; \
	fi
	@if git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
		echo "Error: Tag v$(VERSION) already exists"; \
		exit 1; \
	fi
	@echo ""
	@echo "This will:"
	@echo "  1. Create tag v$(VERSION)"
	@echo "  2. Push to origin (triggers release workflow)"
	@echo "  3. Create GitHub release with notes"
	@echo "  4. Update floating v$$(echo $(VERSION) | cut -d. -f1) tag"
	@echo ""
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@git tag "v$(VERSION)"
	@git push origin "v$(VERSION)"
	@echo ""
	@echo "✓ Tag v$(VERSION) pushed. Release workflow will create the GitHub release."
	@echo "  Watch progress: gh run watch"