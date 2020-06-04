Make sure you have python installed in your computer. 

clone this repo.

Then open cmd and pip install -r requirements.txt

Then in cmd type set FLASK_APP=path to run.py

Initialise database by "flask db init" in cmd

type flask run and you are ready to go.

open http://localhost:5000/register

Subhash just got appointed as the chairman of Festember. He's really happy and wants to celebrate. Ram suggests to organise a booze party at his place. But being a chairman of such a big event, Subhash has too many friends to invite. Help subhash to develop a web application to do the invite job for him.

Normal mode:
Implement an authentication system to allow users to register on the site.
Allow users to schedule an event and create a simple invitation for the same.
Allow creation of simple text based invites with components like Header, Body, Footer etc.
Create dynamic links for invitation which can be visited to view the invitation.
Users must be able to accept / reject invitations.
Support private events - allow the host to send the invitation only to people they wish to invite.
Create a dashboard for a user to view events they have created and invitations they have accepted.
Use prepared statements to prevent SQL injection.
Have a neat, intuitive UI.

Hackermode:
Implement support for customisable invitations (like fonts, colors etc) - Be creative!
Notify users when they receive an invitation, someone accepts their invitation etc.
Add support for user response while accepting invitation. (Like how many people they're bringing, food preferences etc)
Allow the host to set a deadline to accept an invitation.
Have templates for invitations (Birthday Party, Wedding, Funeral etc)
Make the website responsive.

Hackermode++:
Support addition and dynamic placement of images in the invitation.
Implement an attendance tracking system for the events.
Google Calendar API integration for users to keep track of events they're attending.
Use an Email API to send invitations to users via email.
