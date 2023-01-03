# Synthesia Tech Challenge (Platform)

Heya 👋  Thanks for taking the time to do our tech challenge.

One task we often perform at Synthesia is the integration of third-party services and APIs. However, these services can often be error-prone and unreliable, and we need to make sure that our services are resilient against these failures.

For the challenge, we've implemented a simple HTTP API at `https://hiring.api.synthesia.io` with the two following endpoints:

```sql
GET /crypto/sign?message=<YOUR_MESSAGE>
GET /crypto/verify?message=<YOUR_MESSAGE>&signature=<SIGNATURE>
```

The `/crypto/sign` endpoint will cryptographically sign the provided message with a secret RSA key that only we have access to, whereas the `/crypto/verify` endpoint will verify that the provided signature is a valid signature for the provided message.

To simulate an upstream service degradation scenario, we've made the `/crypto/sign` endpoint very unreliable. It will only succeed on the first try about half of the time, and when it fails, you may need to repeatedly try again for a few minutes before the request for a specific message will succeed. Degradation is message-specific, so, if a call with a specific message fails, it does not mean that a call with a different message will also fail.

The challenge is to build and serve a small API that re-exposes our unreliable endpoint in a more reliable way.

We would like the following functionality from your API:

- Expose a `/crypto/sign` endpoint with a similar input syntax to ours.
- Your endpoint **must** always return immediately (within ~2s), regardless of whether the call to our endpoint succeeded.
    - If a result can be provided immediately, include it in the HTTP response with a 200 status code.
    - If a result cannot be provided within the required timeframe, respond with a 202 status code, and notify the user with the result when it is ready. This should be implemented by allowing users of your API to specify a webhook notification URL for each request.
- You **must not** hit our endpoint more than 10 times per minute, but you should expect that your endpoint will get bursts of 60 requests in a minute, and still be able to eventually handle all of those.
- You **must** package your service in such a way that the service can be started as a Docker container or a set of containers with Docker Compose. This will help our engineers when they evaluate your challenge. We *will not* evaluate challenge solutions that are not containerised.
- [Bonus] If your service shuts down and restarts, users who requested a signature before the shutdown should still be notified when their signature is ready without re-requesting one from scratch.

**Getting started**

We don't have any requirements on what stack you use to solve the task, other than the Docker requirement.

When you send requests against our API, you must authorise them with an API key that will be provided to you separately.

Your requests can be authenticated by including the API key as the `Authorization` header:

```sql
Authorization: <YOUR_API_KEY>
```

To verify that your key works correctly, run the following command:

```sql
curl -H "Authorization: <YOUR_API_KEY>" https://hiring.api.synthesia.io/
```

You should see a personalized welcome message for the challenge.

**Timing**

- We're not looking for perfection, rather try to show us something special and have reasons for your decisions.
- Get back to us when you have a timeline for when you are done.

**Where to send the results**

Once you are done please publish the code for your service on a private GitHub repo, share it with [jake@synthesia.io](https://www.notion.so/Synthesia-Tech-Challenge-Platform-7e27a0dddd5e44c29c4c2361668789ef), and send us an email that you’ve submitted a challenge solution.

And of course, let us know if you run into any problems or have any questions.

**Notes**

- Do not spend time trying to understand what is wrong with the endpoint. This will not be useful in solving the challenge. Requests to `/crypto/sign` will sometimes randomly fail, and requests with the same message may take a few minutes to work successfully again.
    - If you see an error code that is not 4xx or 502, and you believe you are querying the API correctly, let us know so we can see if it is an issue with our challenge API.




# Solution
**Instruction**
Run `docker compose up --build` to start the services.
You can accesss http://127.0.0.1:8000/crypto/test_api_key to verify that the provided API key (stored in in .env) is still valid.
You can then access the API on http://127.0.0.1:8000/crypto/sign using the parameters `message` and `callback_url`, e.g.: http://127.0.0.1:8000/crypto/sign?message=This%20is%20a%20test%20Message?&callback_url=https://footy.schubmann.dev/callback/

The background worker is set up to run every 30 seconds - this value can be decreased if you want the retry mechanism to be faster. But as the threshold is 10 requests per minute, this shouldn't change too much.
Messages that are submitted by the user are stored persistently in the database, together with their signatures. If a signature was not yet fulfilled (returned to the user) then the background service will try to return it to the user until it succeeds, even after the whole service restarts or stops.