import constants
import ConfigManager

class UserCache:
    def __init__(self, service):
        self.service = service
        self.cache = ConfigManager.ConfigManager()
        self.cache.read(constants.CACHE_FILE_NAME)
    def get(self, userId, courseId):
        result = self._get(userId)
        if result:
            return result
        self.update(courseId)
        return self._get(userId)
    def _get(self, userId):
        result = self.cache.getstring("teachers", userId)
        if result:
            return result
        result = self.cache.getstring("students", userId)
        if result:
            return result
    def update(self, courseId):
        result = self.service.courses().students().list(courseId=courseId).execute()
        studentInfo = result.get("students", [])
        for student in studentInfo:
            id = student["profile"]["id"]
            self.cache["students"][id] = student["profile"]["name"]["fullName"]
        result = self.service.courses().teachers().list(courseId=courseId).execute()
        teacherInfo = result.get("teachers", [])
        for teacher in teacherInfo:
            id = teacher["profile"]["id"]
            self.cache["teachers"][id] = teacher["profile"]["name"]["fullName"]
    def __del__(self):
        self.cache.write()