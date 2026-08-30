from app.domain.entities import Profile
from app.infrastructure.database.models import ProfileModel


class ProfileMapper:
    @staticmethod
    def to_model(profile: Profile) -> ProfileModel:
        return ProfileModel(
            id=profile.id,
            account_id=profile.account_id,
            display_name=profile.display_name,
            given_name=profile.given_name,
            family_name=profile.family_name,
            bio=profile.bio,
            job_title=profile.job_title,
            organization=profile.organization,
            locale=profile.locale,
            time_zone=profile.time_zone,
            picture_url=profile.picture_url,
            website_url=profile.website_url,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    @staticmethod
    def to_domain(model: ProfileModel) -> Profile:
        profile = Profile(
            account_id=model.account_id,
            display_name=model.display_name,
            given_name=model.given_name,
            family_name=model.family_name,
            bio=model.bio,
            job_title=model.job_title,
            organization=model.organization,
            locale=model.locale,
            time_zone=model.time_zone,
            picture_url=model.picture_url,
            website_url=model.website_url,
        )
        profile.id = model.id
        profile.created_at = model.created_at
        profile.updated_at = model.updated_at
        return profile
