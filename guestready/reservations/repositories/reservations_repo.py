from ..models import Rental, Reservation
from django.db import connection
from datetime import datetime


class ReservationsRepo:
    """
    A repository used to access reservation infromation.
    """

    FORMAT = "%Y-%m-%dT%H-%M-%S"

    def get_with_previous(self):
        """
        Returns a list of dictionaries representing reservations along with their previous reservations.
        """
        result = []
        for r in Reservation.objects.all():
            prev = Reservation.objects.filter(
                checkout__lte=r.checkin, rental_id=r.rental.pk
            ).order_by("-checkin")[:1]
            result.append(
                {
                    "rental_name": r.rental.name,
                    "id": r.pk,
                    "checkin": r.checkin.strftime(ReservationsRepo.FORMAT),
                    "checkout": r.checkout.strftime(ReservationsRepo.FORMAT),
                    "prev": prev.get().pk if len(prev) != 0 else None,
                }
            )
        return result

    def get_with_previous_sql(self):
        """
        For performance reasons, a raw SQL implementation was also added. It implements the same functionality as the
        ORM based implementation.
        """
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT rent.name as rental_name, res1.id, res1.checkin, res1.checkout, (SELECT res2.id FROM reservations_reservation res2
                WHERE res2.rental_id = res1.rental_id and res2.checkout <= res1.checkin ORDER BY res2.checkin DESC LIMIT 1) as prev
                FROM reservations_reservation res1
                JOIN reservations_rental rent ON res1.rental_id == rent.id;
        """
        )
        desc = cursor.description
        res = []
        for row in cursor.fetchall():
            to_insert = {}
            for i, col in enumerate(desc):
                to_insert[col[0]] = (
                    row[i]
                    if not isinstance(row[i], datetime)
                    else row[i].strftime(ReservationsRepo.FORMAT)
                )
            res.append(to_insert)
        return res
