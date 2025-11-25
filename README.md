# Final Project
**Westmont College Fall 2025**

**CS 125 Database Design**

*Assistant Professor* Mike Ryu (mryu@westmont.edu) 

## Author Information
* **Name(s)**: Bailey Fong, James Dodson
* **Email(s)**: bafong@westmont.edu, jdodson@westmont.edu


**Team name:**
- Backcourt

**Who is using this?**
- James’ church youth group, which has small groups, check-in, attendance, among other things.

**What do they want to do?**
- Keep track of attendance, live check-in (which may also be useful for events), small groups, and record small group summaries

**What should they be able to do?**
- Update/change student information, event information, small group info (members, leader(s))

**What shouldn’t they be able to do?**
- Change date-specific small-group info (for example, notes that were taken and attendance that day)
- Change attendance after the day it’s recorded
- Delete past information (events, attendance)


Using Python, we create a connection to our database in Insomnia, and then create a cursor, and by entering in the SQL commands as a string, we can execute any SQL query we want, but we then have to gather and print the results afterwards. However, this means that we can sort all of our data by any metric we want, and get as specific as we need to. Lastly, both the cursor and connection need to be closed so that resources aren't wasted keeping them open for no reason.
