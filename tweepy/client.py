import sys
import requests
from urlparse import urljoin

from tweepy import TweepyError
from tweepy.parsers import JSONParser


class Client(object):

    def __init__(self,
        auth=None,
        host='twitter.com',
        secure=True,
        api_version='1',
        parser=JSONParser(),
        response_format='json'):
        """Create a new client object.

        auth -- A tuple that takes the format:
                    (auth_mode, param_1, param_2, ..., param_n).
                These modes of authentication are supported: OAuth, Basic.
        host -- Hostname of the API server. Defaults to api.twitter.com
        secure -- Uses HTTPS if true (default), otherwise HTTP if false.
        api_version -- Which version of the API to use. Defaults to 1.
        parser -- An instance of the parser which extends the Parser class.
                  By default the JSONParser will be used.
        response_format -- The response format to request from the server.
                           Examples: json (default), xml, rss, atom.
        """
        self.base_url = '%s://%%s.%s/%s/' % \
            ('https' if secure else 'http', host, api_version)

        self.session = requests.session(auth=auth, config={'verbose': sys.stdout})

        # Make sure parser supports response format.
        if parser.supports_format(response_format) is False:
            msg = 'Parse does not support response format: ' + response_format
            raise TweepyError(msg)
        self.parser = parser
        self.response_format = response_format

    def request(self, method, url, parameters=None, files=None, subdomain='api'):
        """Send a request to API server.

        method: type of HTTP method to send (ex: GET, DELETE, POST)
        url: API endpoint URL minus the /<version> part.
        parameters: API parameters to be sent with the request.
        """
        base_url = self.base_url % subdomain
        url = '%s.%s' % (urljoin(base_url, url), self.response_format)

        try:
            r = self.session.request(method, url, params=dict(parameters), files=files)
        except requests.exceptions.RequestException, e:
            raise TweepyError('Request error: %s' % e)

        if r.status_code != 200:
            error_msg = self.parser.parse_error(r.content)
            raise TweepyError('API error: %s' % error_msg)

        if self.parser and len(r.content) > 0:
            return self.parser.parse_content(r.content)
        else:
            return r.content

    def home_timeline(self, **parameters):
        """Returns the most recent statuses, including retweets, posted by
           the authenticating user and the user's they follow.

        Returns: List of status objects.
        """
        return self.request('GET', 'statuses/home_timeline', paramters)

    def mentions(self, **parameters):
        """Returns the most recent mentions (status containing @username) for
           the autenticating user.

        Returns: List of status objects.
        """
        return self.request('GET', 'statuses/mentions', parameters)

    def public_timeline(self, **parameters):
        """Returns the most recent statuses, including retweets, from
           non-protected users. The public timeline is cached for 60 seconds.

        Returns: List of status objects.
        """
        return self.request('GET', 'statuses/public_timeline', parameters)

    def retweeted_by_me(self, **parameters):
        """Returns the most recent retweets posted by the authenticating user.

        Returns: List of status objects.
        """
        return self.request('GET', 'statuses/retweeted_by_me', parameters)

    def retweeted_to_me(self, **parameters):
        """Returns the most recent retweets posted by the users the
           authenticating user follows.

        Returns: List of status objects.
        """
        return self.request('GET', 'statuses/retweeted_to_me', parameters)

    def retweets_of_me(self, **parameters):
        """Returns the most recent tweets of the authenticated user
           that have been retweeted by others.

        Returns: List of status objects.
        """
        return self.request('GET', 'statuses/retweets_of_me', parameters)

    def user_timeline(self, screen_name=None, user_id=None, **parameters):
        """Returns the most recent statuses posted by the authenticating user.
           It is also possible to request another user's timeline by using
           the screen_name or user_id parameter.

        user_id -- (optional) The ID of the user for whom to return
                   results for.
        screen_name -- (optional) The screen name of the user for whom
                       to return results for.

        Returns: List of status objects.
        """
        parameters.update({'screen_name': screen_name, 'user_id': user_id})
        return self.request('GET', 'statuses/user_timeline', parameters)

    def retweeted_to_user(self, id=None, screen_name=None, **parameters):
        """Returns the most recent retweets posted by users the specified user
           follows. Identical to retweeted_to_me, but allows providing user.

        id -- The ID or screen name of the user for whom to return results.
        screen_name -- The screen name of the user for whom to return results.

        Returns: List of status objects.
        """
        parameters.update({'id': id, 'screen_name': screen_name})
        return self.request('GET', 'statuses/retweeted_to_user', parameters)

    def retweeted_by_user(self, id=None, screen_name=None, **parameters):
        """Returns the most recent retweets posted by the specified user.
           Identical to retweeted_by_me except you can choose the user.

        id -- The ID or screen name of the user for whom to return results.
        screen_name -- The screen name of the user for whom to return results.

        Returns: List of status objects.
        """
        parameters.update({'id': id, 'screen_name': screen_name})
        return self.request('GET', 'statuses/retweeted_by_user', parameters)

    def retweeted_by(self, status_id, only_ids=False, **parameters):
        """Show user objects up to 100 members who retweeted the status.

        status_id -- The numerical ID of the desired status.
        only_ids -- (optional) If true only returns the user IDs, otherwise
                    by default user objects will be returned.

        Returns: List of user objects or IDs (if only_ids is true).
        """
        if only_ids:
            url = 'statuses/%s/retweeted_by/ids'
        else:
            url = 'statuses/%s/retweeted_by'
        return self.request('GET', url % status_id, parameters)

    def retweets(self, status_id, **parameters):
        """Returns up to 100 of the first retweets of a given tweet.

        status_id -- The numerical ID of the desired status.

        Returns: List of status objects.
        """
        url = 'statuses/retweets/%s' % status_id
        return self.request('GET', url, parameters)

    def show_status(self, status_id, **parameters):
        """Returns a single status by ID.

        status_id -- The numerical ID of the desired status.

        Returns: A status object.
        """
        url = 'statuses/show/%s' % status_id
        return self.request('GET', url, parameters)

    def destroy_status(self, status_id, **parameters):
        """Destroys the status specified by ID. Authenticating user
           must be the author of the specified status.

        status_id -- The numerical ID of the status to be deleted.

        Returns: A status object which was deleted.
        """
        url = 'statuses/destroy/%s' % status_id
        return self.request('POST', url, parameters)

    def retweet(self, status_id, **parameters):
        """Retweets a tweet. Returns the original tweet with
           retweet details embedded.

        status_id -- The numerical ID of the status to be retweeted.

        Returns: A status object.
        """
        url = 'statuses/retweet/%s' % status_id
        return self.request('POST', url, parameters)

    def update_status(self, status, media=None, **parameters):
        """Updates the authenticating user's status (aka tweeting).

        status -- The text of your status update.
        media -- (optional) A path to a file or a tuple with format:
                    (filename, file-like-object)
                 The file will be uploaded as a media attachment for
                 the new status update. Must be of type supported by
                 the API server (ex: jpg, gif, png).

        Returns: A status object.
        """
        parameters.update({'status': status})

        if isinstance(media, str):
            media = (media, open(media, 'rb'))
        if isinstance(media, tuple):
            return self.request('POST',
                                'statuses/update_with_media',
                                parameters,
                                files={'media[]': media},
                                subdomain='upload')

        return self.request('POST', 'statuses/update', parameters)
