package com.example.gestionstationskii.services;

import com.example.gestionstationskii.entities.Course;
import com.example.gestionstationskii.repositories.ICourseRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@AllArgsConstructor
@Service
public class CourseServicesImpl implements ICourseServices {

    private ICourseRepository courseRepository;

    @Override
    public List<Course> retrieveAllCourses() {
        System.out.println("[INFO] Récupération de tous les cours");
        List<Course> courses = courseRepository.findAll();
        System.out.println("[INFO] Nombre de cours récupérés : " + courses.size());
        return courses;
    }

    @Override
    public Course addCourse(Course course) {
        System.out.println("[INFO] Ajout du cours : " + course);
        Course savedCourse = courseRepository.save(course);
        System.out.println("[INFO] Cours ajouté avec succès : " + savedCourse);
        return savedCourse;
    }

    @Override
    public Course updateCourse(Course course) {
        System.out.println("[INFO] Mise à jour du cours : " + course);
        Course updatedCourse = courseRepository.save(course);
        System.out.println("[INFO] Cours mis à jour avec succès : " + updatedCourse);
        return updatedCourse;
    }

    @Override
    public Course retrieveCourse(Long numCourse) {
        System.out.println("[INFO] Récupération du cours avec ID : " + numCourse);
        Course course = courseRepository.findById(numCourse).orElse(null);
        if (course != null) {
            System.out.println("[INFO] Cours trouvé : " + course);
        } else {
            System.out.println("[WARN] Aucun cours trouvé avec l'ID : " + numCourse);
        }
        return course;
    }
}
