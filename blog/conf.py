STATES = ['draft', 'scheduled', 'deleted', 'published']

POST_STATE_CHOICES = list(zip(range(0, len(STATES)), STATES))