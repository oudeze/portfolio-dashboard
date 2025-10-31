.PHONY: dev backend frontend install

dev: install
	@echo "Starting backend and frontend..."
	@make backend & make frontend

backend:
	@cd backend && uvicorn main:app --reload --port 8000

frontend:
	@cd frontend && npm run dev

install:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

