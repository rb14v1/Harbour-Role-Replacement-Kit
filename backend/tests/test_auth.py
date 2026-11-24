from tests.base import PASSWORD, ApiTestCase


class AuthTests(ApiTestCase):
    def test_register_returns_token_and_user_without_password(self):
        response = self.register("priya@keypass.test", full_name="Priya Raman")
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn("token", body)
        self.assertEqual(body["user"]["email"], "priya@keypass.test")
        self.assertNotIn("password", body["user"])
        self.assertNotIn("password_hash", body["user"])

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.register("dup@keypass.test")
        response = self.register("DUP@keypass.test")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "email_taken")

    def test_short_password_is_rejected(self):
        response = self.api.post(
            "/api/auth/register/",
            {
                "full_name": "Short Pass",
                "email": "short@keypass.test",
                "department": "Engineering",
                "designation": "Frontend Engineer",
                "password": "abc",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_login_succeeds_with_correct_password(self):
        self.register("login@keypass.test")
        response = self.api.post(
            "/api/auth/login/", {"email": "login@keypass.test", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_fails_with_wrong_password(self):
        self.register("wrong@keypass.test")
        response = self.api.post(
            "/api/auth/login/", {"email": "wrong@keypass.test", "password": "not-the-password"}, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "invalid_credentials")

    def test_me_requires_a_token(self):
        response = self.api.get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_returns_current_user_with_valid_token(self):
        self.register("me@keypass.test", full_name="Me Person")
        self.login("me@keypass.test")
        response = self.api.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["full_name"], "Me Person")

    def test_invalid_token_is_rejected(self):
        self.api.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        response = self.api.get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_directory_lists_colleagues_but_not_current_user(self):
        self.register("a@keypass.test", full_name="Alpha", department="Finance", designation="Accountant")
        self.register("b@keypass.test", full_name="Bravo", department="Engineering", designation="Backend Engineer")
        self.login("a@keypass.test")
        response = self.api.get("/api/auth/directory/")
        self.assertEqual(response.status_code, 200)
        names = [person["full_name"] for person in response.json()]
        self.assertEqual(names, ["Bravo"])

    def test_name_with_symbols_or_digits_is_rejected(self):
        for name in ["@@!!", "Priya9", "Mary-Jane", "O'Neil"]:
            with self.subTest(name=name):
                response = self.register("name@keypass.com", full_name=name)
                self.assertEqual(response.status_code, 400)
                self.assertIn("full_name", response.json()["error"]["details"])

    def test_invalid_email_is_rejected(self):
        for email in ["sw@12", "user@keypass", "user.keypass.com"]:
            with self.subTest(email=email):
                response = self.register(email)
                self.assertEqual(response.status_code, 400)

    def test_common_company_domains_are_accepted(self):
        for email in ["a@company.com", "b@charity.org", "c@firm.co.in"]:
            with self.subTest(email=email):
                self.assertEqual(self.register(email).status_code, 201)

    def test_designation_must_belong_to_department(self):
        response = self.register("mismatch@keypass.com", department="Finance", designation="Recruiter")
        self.assertEqual(response.status_code, 400)
        self.assertIn("designation", response.json()["error"]["details"])

    def test_unknown_department_is_rejected(self):
        response = self.register("dept@keypass.com", department="Client Delivery")
        self.assertEqual(response.status_code, 400)
        self.assertIn("department", response.json()["error"]["details"])
