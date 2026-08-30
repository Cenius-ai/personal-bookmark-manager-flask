# Usage

The application runs as a local web server. Once started, open your browser to `http://localhost:5000` for the interactive UI. Below are examples of how to interact with it via HTTP requests.

## Main page (bookmark list)

- **View all bookmarks**  
  `GET /bookmarks` or `GET /` (redirects to `/bookmarks`)

- **Filter by tag**  
  `GET /bookmarks?tag=coding`

- **Add a bookmark** (server‑side form submission)  
  ```bash
  curl -X POST http://localhost:5000/bookmarks \
    -d "title=Flask Docs" \
    -d "url=https://flask.palletsprojects.com" \
    -d "tags=python,web"
  ```
  The form expects fields `title`, `url`, and `tags` (comma-separated). After successful creation, you are redirected back to the list.

- **Edit a bookmark**  
  Click the “Edit” link next to a bookmark, which loads the form with the current values. The edit request is `POST /bookmarks/<id>/edit`:
  ```bash
  curl -X POST http://localhost:5000/bookmarks/1/edit \
    -d "title=Updated Flask Docs" \
    -d "url=https://flask.palletsprojects.com" \
    -d "tags=python,web,framework"
  ```

- **Delete a bookmark**  
  ```bash
  curl -X POST http://localhost:5000/bookmarks/1/delete
  ```

## Stats page

Shows the number of bookmarks per tag.  
```bash
curl http://localhost:5000/stats
```
In the browser, navigate to `/stats`.

## Notes

- All pages are server‑rendered; `curl` examples demonstrate the underlying HTTP API, but normal use is through the web interface.
- No authentication is required — the app is meant for a single user.