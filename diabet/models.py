from django.db import models

# Create your models here.

class Comments(models.Model):
    text = models.CharField(max_length = 500, verbose_name='Предложения и пожелания')

    def __unicode__(self):
        return self.text
    
    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
