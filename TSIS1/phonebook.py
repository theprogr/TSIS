import csv
import json
from pathlib import Path

from connect import connect


def setup_database():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(Path("schema.sql").read_text(encoding="utf-8"))
            cur.execute(Path("procedures.sql").read_text(encoding="utf-8"))
        conn.commit()

    print("Database objects created successfully.")


def get_or_create_group(cur, group_name):
    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,),
    )

    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    return cur.fetchone()[0]


def add_contact():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD: ").strip()
    group_name = input("Group Family/Work/Friend/Other: ").strip() or "Other"
    phone = input("Phone: ").strip()
    phone_type = input("Phone type home/work/mobile: ").strip() or "mobile"

    with connect() as conn:
        with conn.cursor() as cur:
            group_id = get_or_create_group(cur, group_name)

            cur.execute(
                """
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET
                    email = EXCLUDED.email,
                    birthday = EXCLUDED.birthday,
                    group_id = EXCLUDED.group_id
                RETURNING id
                """,
                (name, email, birthday, group_id),
            )

            contact_id = cur.fetchone()[0]

            if phone:
                cur.execute(
                    """
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES (%s, %s, %s)
                    """,
                    (contact_id, phone, phone_type),
                )

        conn.commit()

    print("Contact added/updated.")


def import_csv_file():
    filename = input("CSV file name [contacts.csv]: ").strip() or "contacts.csv"

    with connect() as conn:
        with conn.cursor() as cur:
            with open(filename, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    group_id = get_or_create_group(cur, row["group"])

                    cur.execute(
                        """
                        INSERT INTO contacts(name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name)
                        DO UPDATE SET
                            email = EXCLUDED.email,
                            birthday = EXCLUDED.birthday,
                            group_id = EXCLUDED.group_id
                        RETURNING id
                        """,
                        (
                            row["name"],
                            row["email"],
                            row["birthday"],
                            group_id,
                        ),
                    )

                    contact_id = cur.fetchone()[0]

                    cur.execute(
                        """
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            contact_id,
                            row["phone"],
                            row["type"],
                        ),
                    )

        conn.commit()

    print("CSV imported successfully.")


def show_all_contacts():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.name
                """
            )
            rows = cur.fetchall()

    print_contacts(rows)


def search_contacts_menu():
    query = input("Search text: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()

    print_contacts(rows)


def filter_by_group():
    group_name = input("Group name: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON p.contact_id = c.id
                WHERE LOWER(g.name) = LOWER(%s)
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.name
                """,
                (group_name,),
            )
            rows = cur.fetchall()

    print_contacts(rows)


def sort_contacts():
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")

    choice = input("Choose: ").strip()

    if choice == "1":
        order = "c.name"
    elif choice == "2":
        order = "c.birthday NULLS LAST"
    elif choice == "3":
        order = "c.created_at DESC"
    else:
        print("Invalid choice.")
        return

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    c.name,
                    c.email,
                    c.birthday,
                    g.name,
                    COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY {order}
                """
            )
            rows = cur.fetchall()

    print_contacts(rows)


def add_phone_to_contact():
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Phone type home/work/mobile: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()

    print("Phone added.")


def move_contact_to_group():
    name = input("Contact name: ").strip()
    group_name = input("New group: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()

    print("Contact moved to group.")


def delete_contact():
    name = input("Contact name to delete: ").strip()

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
        conn.commit()

    print("Contact deleted if it existed.")


def export_json():
    filename = input("JSON filename [contacts.json]: ").strip() or "contacts.json"

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.birthday,
                    g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.name
                """
            )

            contacts = []

            for contact_id, name, email, birthday, group_name in cur.fetchall():
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s",
                    (contact_id,),
                )

                phones = [
                    {"phone": phone, "type": phone_type}
                    for phone, phone_type in cur.fetchall()
                ]

                contacts.append(
                    {
                        "name": name,
                        "email": email,
                        "birthday": str(birthday) if birthday else None,
                        "group": group_name,
                        "phones": phones,
                    }
                )

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)

    print("Exported to JSON.")


def import_json():
    filename = input("JSON filename: ").strip()

    with open(filename, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    with connect() as conn:
        with conn.cursor() as cur:
            for contact in contacts:
                name = contact["name"]

                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()

                if existing:
                    action = input(f"{name} exists. skip/overwrite: ").strip().lower()

                    if action == "skip":
                        continue

                    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))

                group_id = get_or_create_group(cur, contact.get("group") or "Other")

                cur.execute(
                    """
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        contact["name"],
                        contact.get("email"),
                        contact.get("birthday"),
                        group_id,
                    ),
                )

                contact_id = cur.fetchone()[0]

                for phone_data in contact.get("phones", []):
                    cur.execute(
                        """
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            contact_id,
                            phone_data["phone"],
                            phone_data["type"],
                        ),
                    )

        conn.commit()

    print("JSON imported.")


def paginated_contacts():
    limit = 3
    offset = 0

    while True:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        c.name,
                        c.email,
                        c.birthday,
                        g.name,
                        COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), '')
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON p.contact_id = c.id
                    GROUP BY c.id, c.name, c.email, c.birthday, g.name
                    ORDER BY c.name
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                rows = cur.fetchall()

        print_contacts(rows)

        command = input("next / prev / quit: ").strip().lower()

        if command == "next":
            offset += limit
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    print("-" * 100)
    print(f"{'Name':15} {'Email':25} {'Birthday':12} {'Group':12} Phones")
    print("-" * 100)

    for name, email, birthday, group_name, phones in rows:
        print(
            f"{str(name):15} "
            f"{str(email or ''):25} "
            f"{str(birthday or ''):12} "
            f"{str(group_name or ''):12} "
            f"{phones}"
        )

    print("-" * 100)


def menu():
    while True:
        print("""
1. Setup database objects
2. Import contacts from CSV
3. Add contact
4. Show all contacts
5. Search contacts
6. Filter by group
7. Sort contacts
8. Add phone to contact
9. Move contact to group
10. Delete contact
11. Export to JSON
12. Import from JSON
13. Paginated contacts
0. Exit
""")

        choice = input("Choose option: ").strip()

        try:
            if choice == "1":
                setup_database()
            elif choice == "2":
                import_csv_file()
            elif choice == "3":
                add_contact()
            elif choice == "4":
                show_all_contacts()
            elif choice == "5":
                search_contacts_menu()
            elif choice == "6":
                filter_by_group()
            elif choice == "7":
                sort_contacts()
            elif choice == "8":
                add_phone_to_contact()
            elif choice == "9":
                move_contact_to_group()
            elif choice == "10":
                delete_contact()
            elif choice == "11":
                export_json()
            elif choice == "12":
                import_json()
            elif choice == "13":
                paginated_contacts()
            elif choice == "0":
                break
            else:
                print("Invalid option.")
        except Exception as error:
            print("ERROR:", error)


if __name__ == "__main__":
    menu()