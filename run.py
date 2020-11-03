from background import mail_reader_thread, mail_processor_thread
from concurrent.futures import ThreadPoolExecutor


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as executor:
        future = executor.submit(mail_reader_thread)
        future = executor.submit(mail_processor_thread)
