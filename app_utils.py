from os import environ

from logstash.formatter import LogstashFormatterBase


class LogstashFormatter(LogstashFormatterBase):
    def format(self, record):
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'message': record.getMessage(),
            'host': self.host,
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,
            'level': record.levelname,
            'logger_name': record.name,
            'pid': record.process,
            'func_name': record.funcName,
            'line': record.lineno,
            'package_version': "1.0.0",
            'process_name': record.processName,
            'thread_name': record.threadName,
            'customer': 'avalon',
            'context': 'computations-logging',
        }

        message.update(self.get_extra_fields(record))
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)
