from django.test import TestCase
from .models import Rental, Reservation
from .repositories import ReservationsRepo
from unittest import skip

# Create your tests here.
class NoPreviousTests(TestCase):
    """
    Tests the ReservationsRepository to check if it works when no previous reservations are present.
    """

    def setUp(self):
        for i in range(5):
            r = Rental.objects.create(name=f"rental-{i}")
            Reservation.objects.create(
                checkin="2022-02-01 00:00:00", checkout="2022-03-01 00:00:00", rental=r
            )

    def test_empty_result(self):
        result = ReservationsRepo().get_with_previous()
        for r in result:
            self.assertEqual(r["prev"], None)

    def test_empty_result_sql(self):
        result_sql = ReservationsRepo().get_with_previous_sql()
        result = ReservationsRepo().get_with_previous()
        self.assertEqual(result, result_sql)


class SinglePrevTest(TestCase):
    """
    Tests the ReservationsRepository to check if it works when multiple reservations are present across many rentals.
    """

    def setUp(self):
        self.prevs = {}
        for i in range(10):
            r = Rental.objects.create(name=f"rental-{i}")
            res1 = Reservation.objects.create(
                checkin="2022-02-01 00:00:00", checkout="2022-03-01 00:00:00", rental=r
            )
            res2 = Reservation.objects.create(
                checkin="2022-03-01 00:00:00", checkout="2022-04-01 00:00:00", rental=r
            )
            self.prevs[res2.pk] = res1.pk

    def test_with_prevs(self):
        result = ReservationsRepo().get_with_previous()
        for r in result:
            target = self.prevs[r["id"]] if r["id"] in self.prevs else None
            self.assertEqual(r["prev"], target)

    def test_with_prevs_sql(self):
        result = ReservationsRepo().get_with_previous_sql()
        for r in result:
            target = self.prevs[r["id"]] if r["id"] in self.prevs else None
            self.assertEqual(r["prev"], target)


class MultiplePrevsTest(TestCase):
    """
    Tests the ReservationsRepository to check if it works when multiple reservations are present across a single rental.
    """

    def setUp(self):
        self.prevs = {}
        self.rental = Rental.objects.create(name=f"rental-unique")
        self.reservations = []
        for i in range(1, 8):
            res = Reservation.objects.create(
                checkin=f"2022-0{i}-01 00:00:00",
                checkout=f"2022-0{i+1}-01 00:00:00",
                rental=self.rental,
            )
            self.reservations.append(res)

    def test_multiple_prevs(self):
        result = ReservationsRepo().get_with_previous()
        for i, r in enumerate(result):
            target = None if i == 0 else self.reservations[i - 1].id
            self.assertEqual(r["prev"], target)

    def test_multiple_prevs_sql(self):
        result = ReservationsRepo().get_with_previous_sql()
        for i, r in enumerate(result):
            target = None if i == 0 else self.reservations[i - 1].id
            self.assertEqual(r["prev"], target)
