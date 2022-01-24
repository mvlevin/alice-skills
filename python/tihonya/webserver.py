from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import logging
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import threading

capabilities = {
    "browserName": "chrome",
    "version": "84.0",
    "enableVNC": False,
    "enableVideo": False
}

driver = webdriver.Remote(
    command_executor="http://51.250.12.170:4444/wd/hub",
    desired_capabilities=capabilities)


def Reload():
    driver.get("http://46.138.253.79:12345")


def WaitButtons():
    print("Waiting until at least one button is on")
    WebDriverWait(driver, 10).until(
            lambda wd: wd.find_element_by_id("stop_button").get_attribute("class") == "on" or wd.find_element_by_id("play_button").get_attribute("class") == "on")


def Play():
    print("Trying to start")
    Reload()
    for retry in range(3):
        button = driver.find_element_by_id("play_button")
        print("Try %d" % (retry + 1))
        button.click()
        Reload()


def Stop():
    print("Trying to stop")
    Reload()
    try:
        WaitButtons()
    except Exception as e:
        logging.error(traceback.format_exc())
    button = driver.find_element_by_id("stop_button")
    for retry in range(3):
        if button.get_attribute("class") == "on":
            print("Try # %d" % (retry + 1))
            button.click()
            Reload()
            button = driver.find_element_by_id("stop_button")
        else:
            break


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = "<html>Success!</html"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        print("Got a get request")
        self._set_headers()
        self.wfile.write(self._html("hi!"))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self.query_string = self.rfile.read(int(self.headers['Content-Length'])).decode('ascii')
        print(self.query_string)
        self.args = dict(cgi.parse_qsl(self.query_string))
        print(self.args)
        if "action" in self.args:            
            if self.args["action"] == "play":
                th = threading.Thread(target=Play)
                th.start()
            elif self.args["action"] == "stop":
                th = threading.Thread(target=Stop)
                th.start()
        self._set_headers()
        self.wfile.write(self._html("POST!"))


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print("Starting httpd server on {%s}:{%d}" % (addr, port))
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
