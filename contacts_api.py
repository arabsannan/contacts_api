import csv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from pathlib import Path

"""
Program: Contacts Manager API
Description: This is a simple FastAPI application to manage contacts. It supports the following operations: create a new contact,
            retrieve all contacts, update a contact, and search for contacts by name or email.
Dependencies: FASTAPI, uvicorn
"""

# Path to the CSV file
CONTACTS_FILE = 'contacts.csv'

# Pydantic model for validating contact data
class Contact(BaseModel):
    name: str
    email: str
    phone: str

# Pydantic model for response data
class ContactInResponse(Contact):
    id: int


app = FastAPI()

@app.get("/api/contacts", response_model=List[ContactInResponse])
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
            "code": 404,
            "message": "No contacts found"
        }
        return JSONResponse(content=response, status_code=404)
        # raise HTTPException(status_code=404, detail="No contacts found.")

    response = {
        "code": 200,
        "data": contacts
    }
    return JSONResponse(content=response, status_code=200)


@app.post("/api/contacts", response_model=ContactInResponse)
async def create_contact(contact: Contact):
    """
    Creates a new contact.

    Args:
        contact (Contact): The contact data to be created.

    Returns:
        ContactInResponse: The created contact's response model.
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
    return new_contact


@app.get("/api/contacts/{id:int}", response_model=ContactInResponse)
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

    return contact


@app.put("/api/contacts/{id}", response_model=ContactInResponse)
async def update_contact(id: int, contact: Contact):
    """
    Update an existing a contact by ID.

    Args:
        id (int): The ID of the contact to retrieve.
        contact (Contact): The updated contact data.

    Returns:
        ContactInResponse: The updated contact's response model  or `None` if no contact with the specified ID exists.
    """
    contacts = retrieve_contacts()
    existing_contact = next(
        (contact for contact in contacts if contact['id'] == id), None)
    if existing_contact is None:
        response = {
            "code": 404,
            "message": "Contact does not exist"
        }
        return JSONResponse(content=response, status_code=404)
        # raise HTTPException(status_code=404, detail="Contact not found")

    existing_contact['name'] = contact.name
    existing_contact['email'] = contact.email
    existing_contact['phone'] = contact.phone
    save_contacts(contacts)
    return existing_contact


@app.get("/api/contacts/search", response_model=List[ContactInResponse])
async def search_contacts(query: str = ""):
    """
    Search for contacts by name or email.

    Args:
        query (str): The search query string.

    Returns:
        List[ContactInResponse]: A list of contacts that match the search query 
                                 in their name or email. If no query is provided, 
                                 all contacts are returned.
    """
    contacts = retrieve_contacts()
    query = query.lower()
    matched_contacts = [contact for contact in contacts if query in contact['name'].lower(
    ) or query in contact['email'].lower()]
    if not matched_contacts:
        response = {
            "code": 404,
            "message": "No match found"
        }
        return JSONResponse(content=response, status_code=404)
    return matched_contacts


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
                    'id': int(row['id']),
                    'name': row['name'],
                    'email': row['email'],
                    'phone': row['phone']
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
