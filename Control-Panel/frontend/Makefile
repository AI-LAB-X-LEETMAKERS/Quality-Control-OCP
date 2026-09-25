run:
	@hostname -I | awk '{print $$1}' | xargs -I {} echo "http://{}:3000"
	python3 -m http.server 3000
	
host:
	ngrok http 3000