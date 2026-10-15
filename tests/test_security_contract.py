from app.models import ApplicationStatus, VacancyStatus


def test_terminal_vacancy_statuses_are_distinct():
    assert VacancyStatus.published != VacancyStatus.pending


def test_application_statuses_include_offer_without_employment_claim():
    assert ApplicationStatus.offer.value == "offer"
    assert ApplicationStatus.accepted.value == "accepted"
