FROM python:3.12
WORKDIR /home/app

# Dependencies
COPY --chmod=744 requirements.txt .
RUN pip install -r requirements.txt
COPY --chmod=744 .env .

# Source code
RUN useradd -ms /bin/bash app
COPY --chmod=777 backend ./backend
RUN chown -R app:app .
EXPOSE 5000
USER app

# Necessary Script Directory
WORKDIR backend/server
CMD ["flask", "run", "--port", "5000"]
