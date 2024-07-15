import unittest
from fastapi.testclient import TestClient
from urlShortener.main import app, url_library


class TestUrl(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        url_library.clear()

    # testing that a url is successfully added
    def test_add_only_url(self):
        data = {"original_url": "https://www.example.com"}
        response = self.client.post(
            "/shorten_url",
            json= data
        )

        saved_data = url_library[dict(response.json())['short_url']]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["short_url"], saved_data['short_url'])
        self.assertEqual(data["original_url"], str(saved_data["original_url"])[:-1])

    # testing that a url is added with a user defined shortened url
    def test_add_url_and_shorten(self):
        shorten_url = "test_url"
        data = {"original_url": "https://www.example.com"}
        response = self.client.post(
            f"/shorten_url?short_url={shorten_url}",
            json=data
        )

        saved_data = url_library[dict(response.json())['short_url']]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["short_url"], shorten_url)
        self.assertEqual(data["original_url"], str(saved_data["original_url"])[:-1])

    # testing that the passed in url has the correct HttpUrl format
    def test_valid_format(self):
        urls = ["www.example.com", "google.com", "target.com"]
        for url in urls:
            data = {"original_url": url}
            response = self.client.post(
                "/shorten_url",
                json= data
            )
            self.assertNotEqual(response.status_code, 200)
            self.assertEqual(response.json()["detail"], "Value must start 'http://' or 'https://'")

    # testing nonexistent sites and sites with typos will not be stored
    def test_invalid_url(self):
        urls = ["https://www.cooom.com", "https://www.test.cooom.com", "https://www.nonexistentwebsite1234567890.com","https://www.exmaple.com"]
        for url in urls:
            data = {"original_url": url}
            response = self.client.post(
                "/shorten_url",
                json= data
            )
            self.assertNotEqual(response.status_code, 200)
            self.assertEqual(response.json()["detail"], "Invalid URL")


    # adding two user defined urls with the same shortened url
    def test_existing_url(self):
        shorten_url = "test_url"
        data = {"original_url": "https://www.example.com"}
        first_post = self.client.post(
            f"/shorten_url?short_url={shorten_url}",
            json=data
        )

        response = self.client.post(
            f"shorten_url?short_url={shorten_url}",
            json=data
        )

        self.assertEqual(response.status_code, 404)
        self.assertAlmostEqual(response.json()["detail"], f"Short URL '{shorten_url}' already exists.")

    # testing the listing all API, when there are links present
    def test_listing_all(self):
        urls = ["https://www.example.com", "https://www.target.com", "https://www.artwod.com", "https://artwod.com"]
        for url in urls:
            data = {"original_url": url}
            response = self.client.post(
                "/shorten_url",
                json= data
            )

            self.assertEqual(response.status_code, 200)

        response = self.client.get("/list_urls")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), len(urls))

    # testing list all with an empty DB
    def test_empty_db(self):
        response = self.client.get("/list_urls")
        self.assertEqual(response.status_code, 404)
        self.assertAlmostEqual(response.json()['detail'], "No URLs available.")

    # testing that the redirection works for a valid site found in the db
    def test_redirection(self):
        data = {
            "original_url":"https://www.example.com"
        }
        response = self.client.post(
            "/shorten_url?short_url=tiny2",
            json= data
        )
        saved_data = url_library[dict(response.json())['short_url']]

        assert "tiny2" in url_library

        response = self.client.get("/redirect/tiny2", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(data["original_url"], str(saved_data["original_url"])[:-1])

    # testing with a call to a short_url that does not exist
    def test_unavailable_short_url(self):
        data = {
            "original_url":"https://www.example.com"
        }

        self.client.post(
            "/shorten_url",
            json= data
        )

        short_url = "tiny2"
        response = self.client.get(f"/redirect/{short_url}", follow_redirects=False)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], f"No URL found for '{short_url}' short url provided.")

if __name__ == '__main__':
    unittest.main()