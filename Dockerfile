FROM python:3.12
WORKDIR /home/app

# Dependencies
COPY --chmod=744 requirements.txt .
COPY --chmod=744 .env .
COPY --chmod=744 gunicorn.conf.py .
RUN pip install -r requirements.txt

# Source code
RUN useradd -ms /bin/bash app
COPY --chmod=777 backend ./backend
RUN chown -R app:app .
EXPOSE 3003
USER app

CMD ["gunicorn", "-c", "gunicorn.conf.py"]
#CMD ["bash"]