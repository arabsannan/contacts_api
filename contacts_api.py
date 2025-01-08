import csv
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr

"""
Program: Contacts Manager API
Description: This is a simple FastAPI application to manage contacts. It supports the following 
                operations: create a new contact, update a contact, and search for contacts
                by name or email.
"""

# Path to the CSV file
CONTACTS_FILE = 'contacts.csv'

# Pydantic model for validating contact data


class Contact(BaseModel):
    name: str = Field(..., min_length=2, max_length=50,
                      description="Contact's name")
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=10, max_length=15,
                       description="Contact's phone number")


app = FastAPI()


@app.post("/api/contacts")
async def create_contact(contact: Contact):
    """
    Creates a new contact.

    Args:
        contact (Contact): The contact data to be created.

    Returns:
        JSONResponse: Contains a success message and created contact's data.

    Note:
        The `save_contacts` function saves a list of contact dictionaries to the CSV file.
    """
    contacts = retrieve_contacts()
    contact_id = max([contact['id'] for contact in contacts], default=0) + 1
    new_contact = {
        'id': contact_id,
        'name': contact.name,
        'email': contact.email,
        'phone': contact.phone
    }
    contacts.append(new_contact)
    save_contacts(contacts)
    response = {
        "code": 200,
        "message": "Contact created successfully",
        "data": new_contact
    }
    return JSONResponse(content=response, status_code=200)


@app.put("/api/contacts/{id}")
async def update_contact(id: int, contact: Contact):
    """
    Update an existing a contact by ID.

    Args:
        id (int): The ID of the contact to retrieve.
        contact (Contact): The updated contact data.

    Returns:
        JSONResponse: Contains a success message and updated contact's data or 
                    an empty array if no contact with the specified ID exists.
    """
    contacts = retrieve_contacts()
    existing_contact = next(
        (contact for contact in contacts if contact['id'] == id), None)
    if existing_contact is None:
        response = {
            "code": 404,
            "message": "Contact does not exist",
            "data": []
        }
        return JSONResponse(content=response, status_code=404)

    existing_contact['name'] = contact.name
    existing_contact['email'] = contact.email
    existing_contact['phone'] = contact.phone
    save_contacts(contacts)
    response = {
        "code": 200,
        "message": "Contact updated successfully",
        "data": existing_contact
    }
    return JSONResponse(content=response, status_code=200)


@app.get("/api/contacts/search")
async def search_contacts(query: str = ""):
    """
    Search for contacts by name or email.

    Args:
        query (str): The search query string.

    Returns:
        JSONResponse: Contains the data of contacts that match the search query in 
                their name or email. If no query is provided, all contacts are returned.
    """
    contacts = retrieve_contacts()
    query = query.lower()
    matched_contacts = [contact for contact in contacts if query in
                        contact['name'].lower() or query in contact['email'].lower()]
    if not matched_contacts:
        response = {
            "code": 200,
            "message": "No match found",
            "data": []
        }
        return JSONResponse(content=response, status_code=200)

    response = {
        "code": 200,
        "message": "Contacts retrieved successfully",
        "data": matched_contacts
    }
    return JSONResponse(content=response, status_code=200)


@app.get("/api/contacts/{id:int}")
async def get_contact(id: int):
    """
    Retrieve an existing a contact by ID.

    Args:
        id (int): The ID of the contact to retrieve.

    Returns:
        ContactInResponse: The retrieved contact's response model.
        JSONResponse: A JSON response with a 404 status code and an error message 
                    if no contact with the specified ID is found.
    """
    contacts = retrieve_contacts()
    contact = next(
        (contact for contact in contacts if contact['id'] == id), None)
    if contact is None:
        response = {
            "code": 404,
            "message": "Contact does not exist"
        }
        return JSONResponse(content=response, status_code=404)

    response = {
        "code": 200,
        "message": "Contact retrieved successfully",
        "data": contact
    }
    return JSONResponse(content=response, status_code=200)


@app.get("/api/contacts")
def get_all_contacts():
    """
    Get the list of all contacts stored in csv file.

    Returns:
        JSONResponse: A response object containing the contacts data and a 200 HTTP status code.

    Raises:
        HTTPException: If the contacts cannot be retrieved, a 404 HTTP status code is returned.
    """
    contacts = retrieve_contacts()

    if not contacts:
        response = {
            "code": 200,
            "message": "No contacts found",
            "data": []
        }
        return JSONResponse(content=response, status_code=200)

    response = {
        "code": 200,
        "message": "Contacts retrieved successfully",
        "data": contacts
    }
    return JSONResponse(content=response, status_code=200)


def retrieve_contacts():
    """
    Helper function to retrieve contacts from the csv file.

    Returns:
        List[Contact]: A list of contact objects.
    """
    contacts = []
    if Path(CONTACTS_FILE).exists():
        with open(CONTACTS_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                contacts.append({
                    'id': int(row.get('id')),
                    'name': row.get('name'),
                    'email': row.get('email'),
                    'phone': row.get('phone')
                })
    return contacts


def save_contacts(contacts):
    """
    Helper function to save a list of contact dictionaries to the CSV file.

    Args:
        contacts (List[dict]): A list of dictionaries, where each dictionary represents a contact.
    Returns:
        None: This function does not return any value.
        """
    with open(CONTACTS_FILE, mode='w', newline='') as file:
        header_names = ['id', 'name', 'email', 'phone']
        writer = csv.DictWriter(file, fieldnames=header_names)
        writer.writeheader()
        for contact in contacts:
            writer.writerow(contact)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8800)
