# Virtual CV (Django + Vercel)

Public site for everyone, edited only through the Django admin by you.

## Run locally
```
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations portfolio
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/admin/ (DEBUG defaults to on locally), add your Profile, Education, Achievements, Projects.
Commit the generated `portfolio/migrations/0001_initial.py`.

## Deploy to Vercel
1. Create a free Postgres DB (Neon or Supabase) and a public storage bucket (Supabase Storage with S3 access).
2. Push this folder to GitHub and import it in Vercel.
3. Add the variables from `.env.example` in Vercel (set DEBUG=0, a long SECRET_KEY, and a private ADMIN_URL such as `manage-k39x/`).
4. Collect static files locally and commit them, because Vercel's disk is read-only:
   `python manage.py collectstatic --noinput` then commit the `staticfiles/` folder.
5. Create the tables and your admin user in production, from your computer:
   `DATABASE_URL=<prod url> python manage.py migrate` then `DATABASE_URL=<prod url> python manage.py createsuperuser`
6. Redeploy. Your site is at your-project.vercel.app and the admin at /<ADMIN_URL>.

## Uploading big files
Vercel limits a request body to about 4.5 MB, so large uploads through the live admin will fail.
For big photos or PDFs, run the admin locally with the production variables set
(`python manage.py runserver` with DATABASE_URL and S3_* exported). Files still land in the live bucket.
