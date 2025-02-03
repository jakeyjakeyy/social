from django.core.management.base import BaseCommand
from django.conf import settings
from social.models import ImagePost
import os
from datetime import datetime
import shutil


class Command(BaseCommand):
    help = "Moves existing images into user specific folders (or adjust the code to any directory)"

    def handle(self, *args, **options):
        image_posts = ImagePost.objects.all()
        moved_count = 0
        errors = []

        for post in image_posts:
            try:
                old_path = os.path.join(settings.MEDIA_ROOT, str(post.image))

                if "users" in old_path:
                    continue

                username = post.post.account.user.username
                filename = os.path.basename(old_path.split("/")[-1])
                new_relative_path = f'users/{username}/images/{datetime.now().strftime("%Y/%m/%d")}/{filename}'
                new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)

                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

                if os.path.exists(old_path):
                    shutil.move(old_path, new_full_path)

                    post.image = new_relative_path
                    post.save()

                    moved_count += 1
                    self.stdout.write(f"Moved: {old_path} -> {new_full_path}")
                else:
                    errors.append(f"File not found: {old_path}")

            except Exception as e:
                errors.append(f"Error processing {post.id}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f"Moved {moved_count} files"))
        if errors:
            self.stdout.write(self.style.WARNING("Errors:"))
            for error in errors:
                self.stdout.write(self.style.ERROR(error))
