# Version from file
VERSION := $(shell cat version.txt)

## Tag this version and publish it: the release is the website (tools/site/deploy_site.sh)
.PHONY: tag
tag:
	@! git rev-parse -q --verify refs/tags/$(VERSION) >/dev/null || { echo "Tag $(VERSION) already exists" >&2; exit 1; }
	tools/site/deploy_site.sh && \
	git tag $(VERSION) && git push origin $(VERSION) && \
	echo "Tagged and published: $(VERSION)"
