package com.example.gestionstationskii.services;

import com.example.gestionstationskii.entities.*;
import com.example.gestionstationskii.repositories.*;
import com.example.gestionstationskii.repositories.IInstructorRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
@AllArgsConstructor
@Service
public class InstructorServicesImpl implements IInstructorServices {

    private IInstructorRepository instructorRepository;
    private ICourseRepository courseRepository;

    @Override
    public Instructor addInstructor(Instructor instructor) {
        System.out.println("=== [Instructor Service] Ajout d’un nouvel instructeur ===");
        System.out.println("Nom : " + instructor.getFirstName() + " " + instructor.getLastName());
        Instructor savedInstructor = instructorRepository.save(instructor);
        System.out.println("✅ Instructeur ajouté avec succès (ID : " + savedInstructor.getNumInstructor() + ")");
        return savedInstructor;
    }

    @Override
    public List<Instructor> retrieveAllInstructors() {
        System.out.println("=== [Instructor Service] Récupération de tous les instructeurs ===");
        List<Instructor> instructors = instructorRepository.findAll();
        System.out.println("Nombre total d’instructeurs trouvés : " + instructors.size());
        return instructors;
    }

    @Override
    public Instructor updateInstructor(Instructor instructor) {
        System.out.println("=== [Instructor Service] Mise à jour d’un instructeur ===");
        System.out.println("Instructeur ID : " + instructor.getNumInstructor());
        Instructor updatedInstructor = instructorRepository.save(instructor);
        System.out.println("✅ Instructeur mis à jour avec succès.");
        return updatedInstructor;
    }

    @Override
    public Instructor retrieveInstructor(Long numInstructor) {
        System.out.println("=== [Instructor Service] Récupération d’un instructeur ===");
        System.out.println("Recherche de l’instructeur avec ID : " + numInstructor);
        Instructor instructor = instructorRepository.findById(numInstructor).orElse(null);
        if (instructor != null) {
            System.out.println("✅ Instructeur trouvé : " + instructor.getFirstName() + " " + instructor.getLastName());
        } else {
            System.out.println("⚠️ Aucun instructeur trouvé avec l’ID : " + numInstructor);
        }
        return instructor;
    }

    @Override
    public Instructor addInstructorAndAssignToCourse(Instructor instructor, Long numCourse) {
        System.out.println("=== [Instructor Service] Ajout d’un instructeur et assignation à un cours ===");
        System.out.println("Cours cible ID : " + numCourse);
        Course course = courseRepository.findById(numCourse).orElse(null);

        if (course == null) {
            System.out.println("⚠️ Cours introuvable avec l’ID : " + numCourse);
            return null;
        }

        Set<Course> courseSet = new HashSet<>();
        courseSet.add(course);
        instructor.setCourses(courseSet);

        Instructor savedInstructor = instructorRepository.save(instructor);
        System.out.println("✅ Instructeur ajouté et assigné au cours (ID : " + course.getNumCourse() + ")");
        return savedInstructor;
    }
}
