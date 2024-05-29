#!/usr/bin/make

shell:
	docker-compose -f docker-compose.yml exec -u 0 chatbot-api bash

up:
	docker-compose -f docker-compose.yml up --build -d

down:
	docker-compose -f docker-compose.yml down

log:
	docker logs --follow moc-scripts