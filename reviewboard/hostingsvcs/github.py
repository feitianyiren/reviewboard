import httplib
import urllib2
from django.utils import simplejson
from reviewboard.hostingsvcs.service import HostingService
from reviewboard.scmtools.errors import FileNotFoundError
                                 '%(github_public_repo_name)s/issues#issue/%%s',
    supports_bug_trackers = True
    RAW_MIMETYPE = 'application/vnd.github.v3.raw'

            repo_info = self._api_get_repository(
                self._get_repository_owner_raw(plan, kwargs),
                self._get_repository_name_raw(plan, kwargs))
        except Exception, e:
            if str(e) == 'Not Found':
                        _('A repository with this organization or name was not '
                          'found.'))
            rsp, headers = self._json_post(
                body=simplejson.dumps(body))
        except (urllib2.HTTPError, urllib2.URLError), e:
                rsp = simplejson.loads(data)
                raise AuthorizationError(str(e))
                except HostingServiceError, e:
                    if str(e) != 'Not Found':
        url = self._build_api_url(self._get_repo_api_url(repository),
                                  'git/blobs/%s' % revision)
            return self._http_get(url, headers={
                'Accept': self.RAW_MIMETYPE,
            })[0]
        except (urllib2.URLError, urllib2.HTTPError):
            raise FileNotFoundError(path, revision)
    def get_file_exists(self, repository, path, revision, *args, **kwargs):
        url = self._build_api_url(self._get_repo_api_url(repository),
                                  'git/blobs/%s' % revision)
        try:
            self._http_get(url, headers={
                'Accept': self.RAW_MIMETYPE,
            })
            return True
        except (urllib2.URLError, urllib2.HTTPError):
            return False
        return self._api_post(url=url,
                              username=client_id,
                              password=client_secret)
        self._api_delete(url=url,
                         headers=headers,
                         username=self.account.username,
                         password=password)
    def _get_api_error_message(self, rsp, status_code):
        """Return the error(s) reported by the GitHub API, as a string

        See: http://developer.github.com/v3/#client-errors
        """
        if 'message' not in rsp:
            msg = _('Unknown GitHub API Error')
        elif 'errors' in rsp and status_code == httplib.UNPROCESSABLE_ENTITY:
            errors = [e['message'] for e in rsp['errors'] if 'message' in e]
            msg = '%s: (%s)' % (rsp['message'], ', '.join(errors))
        else:
            msg = rsp['message']

        return msg

    def _http_get(self, url, *args, **kwargs):
        data, headers = super(GitHub, self)._http_get(url, *args, **kwargs)
        self._check_rate_limits(headers)
        return data, headers

    def _http_post(self, url, *args, **kwargs):
        data, headers = super(GitHub, self)._http_post(url, *args, **kwargs)
        self._check_rate_limits(headers)
        return data, headers

    def _check_rate_limits(self, headers):
        rate_limit_remaining = headers.get('X-RateLimit-Remaining', None)

        try:
            if (rate_limit_remaining is not None and
                int(rate_limit_remaining) <= 100):
                logging.warning('GitHub rate limit for %s is down to %s',
                                self.account.username, rate_limit_remaining)
        except ValueError:
            pass

        return '%s?access_token=%s' % (
            '/'.join(api_paths),
            self.account.data['authorization']['token'])
                                   owner, repo_name)
    def _api_get_repository(self, owner, repo_name):
        return self._api_get(self._build_api_url(
            self._get_repo_api_url_raw(owner, repo_name)))
    def _api_get(self, url, *args, **kwargs):
        try:
            data, headers = self._json_get(url, *args, **kwargs)
            return data
        except (urllib2.URLError, urllib2.HTTPError), e:
            self._check_api_error(e)
    def _api_post(self, url, *args, **kwargs):
        try:
            data, headers = self._json_post(url, *args, **kwargs)
            return data
        except (urllib2.URLError, urllib2.HTTPError), e:
            self._check_api_error(e)
    def _api_delete(self, url, *args, **kwargs):
        try:
            data, headers = self._json_delete(url, *args, **kwargs)
            return data
        except (urllib2.URLError, urllib2.HTTPError), e:
            self._check_api_error(e)
    def _check_api_error(self, e):
        data = e.read()
        try:
            rsp = simplejson.loads(data)
        except:
            rsp = None
        if rsp and 'message' in rsp:
            response_info = e.info()
            x_github_otp = response_info.get('X-GitHub-OTP', '')
            if x_github_otp.startswith('required;'):
                raise TwoFactorAuthCodeRequiredError(
                    _('Enter your two-factor authentication code. '
                      'This code will be sent to you by GitHub.'))
            if e.code == 401:
                raise AuthorizationError(rsp['message'])
            raise HostingServiceError(rsp['message'])
        else:
            raise HostingServiceError(str(e))