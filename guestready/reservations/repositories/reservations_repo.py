from ..models import Reservation
from django.db import connection
from django.db.models import OuterRef, Subquery, F
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

        # Here is the generated query from the ORM
        # SELECT "reservations_reservation"."id", "reservations_reservation"."checkin", "reservations_reservation"."checkout", "reservations_reservation"."rental_id",
        # (SELECT U0."id" FROM "reservations_reservation" U0
        # 	WHERE (U0."checkout" <= ("reservations_reservation"."checkin") AND U0."rental_id" = ("reservations_reservation"."rental_id"))
        # 	ORDER BY U0."checkin" DESC LIMIT 1) AS "prev",
        # "reservations_rental"."name" AS "rental_name"
        # FROM "reservations_reservation" INNER JOIN "reservations_rental" ON ("reservations_reservation"."rental_id" = "reservations_rental"."id")

        sq = Reservation.objects.filter(
            rental_id=OuterRef("rental_id"), checkout__lte=OuterRef("checkin")
        ).order_by("-checkin")
        reservations = Reservation.objects.all()
        reservations = reservations.annotate(prev=Subquery(sq.values("pk")[:1]))
        reservations = reservations.annotate(rental_name=F("rental__name"))
        reservations = list(reservations)
        result = [
            {
                "rental_name": r.rental_name,
                "id": r.pk,
                "checkin": r.checkin.strftime(ReservationsRepo.FORMAT),
                "checkout": r.checkout.strftime(ReservationsRepo.FORMAT),
                "prev": r.prev,
            }
            for r in reservations
        ]
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
